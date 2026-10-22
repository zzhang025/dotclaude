#!/usr/bin/env python3
"""Export, plan and apply Azure DevOps requirement hierarchies.

Hierarchy: Epic > User Story > System Requirement > Software Requirement,
with Test Cases linked to the requirements they cover ("Tested By").

Commands
  export  --root ID [--root ID ...] --out FILE
          Read an existing Epic or User Story tree into a requirements file.
  plan    --file FILE [--map MAP] [--review OUT.md]
          Compare the file with ADO and list what would be created or changed.
          Read-only. --review writes a Now/Proposed markdown review.
  apply   --file FILE [--map MAP] [--backup DIR] [--force]
          Create and update work items, then verify them. Items whose ADO
          revision changed since export are skipped unless --force.
  verify  --file FILE [--map MAP]
          Check that ADO matches the file.

Authentication uses `az account get-access-token`, or a PAT in ADO_PAT.
Standard library only.
"""

import argparse
import base64
import datetime
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ADO_RESOURCE = "499b84ac-1321-427f-aa17-267ca6975798"
API = "api-version=7.1"
PARENT = "System.LinkTypes.Hierarchy-Reverse"
CHILD = "System.LinkTypes.Hierarchy-Forward"
TESTS = "Microsoft.VSTS.Common.TestedBy-Reverse"  # test case -> requirement it tests
TESTED_BY = "Microsoft.VSTS.Common.TestedBy-Forward"  # requirement -> its test cases
TYPES = {
    "story": "User Story",
    "sys": "System Requirement",
    "sw": "Software Requirement",
    "test": "Test Case",
}
PREFIX = {"story": "US", "sys": "SYS", "sw": "SW", "test": "TC"}
# Node property -> ADO field. Text fields are stored as plain text in the file and HTML in ADO.
TEXT_FIELDS = {
    "title": "System.Title",
    "description": "System.Description",
    "acceptanceCriteria": "Microsoft.VSTS.Common.AcceptanceCriteria",
    "solutionDesign": "Custom.SolutionDesign",
}
STEPS_FIELD = "Microsoft.VSTS.TCM.Steps"
GO_LIVE_FIELD = "Custom.GoLiveBlocker"

sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- text <-> HTML

def html_to_text(value):
    """Convert ADO rich text to plain paragraphs; list items become '- ' lines."""
    if not value:
        return ""
    text = re.sub(r"(?i)<li[^>]*>", "\n- ", value)
    text = re.sub(r"(?i)<br\s*/?>|</(p|div|li|ul|ol|h\d|tr)>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    out, blank = [], False
    for line in lines:
        if not line:
            blank = bool(out)
            continue
        if blank and not line.startswith("- "):
            out.append("")
        blank = False
        out.append(line)
    return "\n".join(out).strip()


def text_to_html(value):
    """Blank-line separated paragraphs become <p>; consecutive '- ' lines become a list."""
    if not value:
        return ""
    parts = []
    for block in re.split(r"\n\s*\n", value.strip()):
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        items = [line[2:] for line in lines if line.startswith("- ")]
        lead = [line for line in lines if not line.startswith("- ")]
        if lead:
            parts.append("<p>" + "<br>".join(html.escape(line, quote=False) for line in lead) + "</p>")
        if items:
            parts.append("<ul>" + "".join(f"<li>{html.escape(i, quote=False)}</li>" for i in items) + "</ul>")
    return "".join(parts)


def same_text(a, b):
    squash = lambda s: re.sub(r"\s+", " ", (s or "").replace("- ", "")).strip()
    return squash(a) == squash(b)


def is_rich(value):
    return bool(value and re.search(r"(?i)<(table|img|h\d|pre|code)\b", value))


def steps_from_xml(value):
    if not value:
        return []
    steps = []
    for step in re.findall(r"(?s)<step\b.*?</step>", value):
        strings = re.findall(r"(?s)<parameterizedString[^>]*>(.*?)</parameterizedString>", step)
        strings = [html_to_text(html.unescape(s)) for s in strings] + ["", ""]
        steps.append({"action": strings[0], "expected": strings[1]})
    return steps


def steps_to_xml(steps):
    parts = [f'<steps id="0" last="{len(steps) + 1}">']
    for n, step in enumerate(steps, start=2):
        action = html.escape(text_to_html(step.get("action", "")))
        expected = html.escape(text_to_html(step.get("expected", "")))
        parts.append(f'<step id="{n}" type="ValidateStep">'
                     f'<parameterizedString isformatted="true">{action}</parameterizedString>'
                     f'<parameterizedString isformatted="true">{expected}</parameterizedString>'
                     "<description /></step>")
    parts.append("</steps>")
    return "".join(parts)


def same_steps(a, b):
    norm = lambda steps: [(re.sub(r"\s+", " ", s.get("action", "")).strip(),
                           re.sub(r"\s+", " ", s.get("expected", "")).strip()) for s in steps or []]
    return norm(a) == norm(b)


# ---------------------------------------------------------------- ADO client

class Ado:
    def __init__(self, organization, project):
        self.base = f"https://dev.azure.com/{organization}/{urllib.parse.quote(project)}/_apis/wit"
        self.org_base = f"https://dev.azure.com/{organization}"
        self.headers = {"Authorization": self._auth()}

    @staticmethod
    def _auth():
        pat = os.environ.get("ADO_PAT")
        if pat:
            return "Basic " + base64.b64encode(f":{pat}".encode()).decode()
        try:
            token = subprocess.run(
                ["az", "account", "get-access-token", "--resource", ADO_RESOURCE, "--query", "accessToken", "-o", "tsv"],
                capture_output=True, text=True, check=True, shell=os.name == "nt").stdout.strip()
        except (OSError, subprocess.CalledProcessError) as error:
            sys.exit(f"Could not get an Azure DevOps token. Run 'az login' or set ADO_PAT. ({error})")
        return f"Bearer {token}"

    def request(self, method, url, body=None, content_type="application/json"):
        data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
        headers = dict(self.headers)
        if data is not None:
            headers["Content-Type"] = content_type
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read() or b"null")
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")
            raise RuntimeError(f"{method} {url} failed ({error.code}): {detail[:500]}") from None

    def get_items(self, ids):
        ids = sorted({int(i) for i in ids})
        found = {}
        for start in range(0, len(ids), 200):
            body = {"ids": ids[start:start + 200], "$expand": "relations", "errorPolicy": "omit"}
            for item in self.request("POST", f"{self.base}/workitemsbatch?{API}", body)["value"]:
                if item:
                    found[item["id"]] = item
        return found

    def create(self, work_item_type, ops):
        url = f"{self.base}/workitems/${urllib.parse.quote(work_item_type)}?{API}"
        return self.request("POST", url, ops, "application/json-patch+json")

    def patch(self, item_id, ops):
        return self.request("PATCH", f"{self.base}/workitems/{item_id}?{API}", ops, "application/json-patch+json")

    def upload(self, path):
        url = f"{self.base}/attachments?fileName={urllib.parse.quote(Path(path).name)}&{API}"
        return self.request("POST", url, Path(path).read_bytes(), "application/octet-stream")["url"]

    def item_url(self, item_id):
        return f"{self.base}/workItems/{item_id}"


def related_ids(item, rel):
    return [int(r["url"].rsplit("/", 1)[1]) for r in item.get("relations") or [] if r["rel"] == rel]


# ---------------------------------------------------------------- requirements file

def iter_nodes(doc):
    """Yield (kind, node, parent_node_or_None, story) in creation order."""
    for story in doc.get("stories", []):
        yield "story", story, None, story
        for sys_req in story.get("systemRequirements", []):
            yield "sys", sys_req, story, story
            for sw in sys_req.get("softwareRequirements", []):
                yield "sw", sw, sys_req, story
    for story in doc.get("stories", []):
        for test in story.get("testCases", []):
            yield "test", test, None, story


def node_key(kind, node):
    return node.get("key") or (f"{PREFIX[kind]}-{node['id']}" if node.get("id") else None)


def load_map(path):
    return json.loads(Path(path).read_text(encoding="utf-8")) if path and Path(path).exists() else {}


def save_map(path, mapping):
    if path:
        Path(path).write_text(json.dumps(mapping, indent=2, sort_keys=True), encoding="utf-8")


def resolve_id(kind, node, mapping):
    return node.get("id") or mapping.get(node_key(kind, node))


def validate(doc):
    problems, keys = [], {}
    for kind, node, _, _ in iter_nodes(doc):
        key = node_key(kind, node)
        if not key:
            problems.append(f"A {TYPES[kind]} has neither 'key' nor 'id': {node.get('title', '?')}")
            continue
        if key in keys:
            problems.append(f"Duplicate key {key}")
        keys[key] = kind
        if not node.get("title"):
            problems.append(f"{key} has no title")
    for kind, node, _, _ in iter_nodes(doc):
        if kind == "test":
            for covered in node.get("covers", []):
                if covered not in keys:
                    problems.append(f"{node_key(kind, node)} covers unknown key {covered}")
            if not node.get("covers"):
                problems.append(f"{node_key(kind, node)} covers nothing")
    if problems:
        sys.exit("Requirements file problems:\n  " + "\n  ".join(problems))
    return keys


# ---------------------------------------------------------------- export

def export(args):
    ado = Ado(args.organization, args.project)
    roots = ado.get_items(args.root)
    missing = set(args.root) - set(roots)
    if missing:
        sys.exit(f"Not found or no access: {sorted(missing)}")
    doc = {"ado": {"organization": args.organization, "project": args.project}, "stories": []}
    stories = []
    for root in roots.values():
        kind = root["fields"]["System.WorkItemType"]
        if kind == "Epic":
            doc["ado"]["epicId"] = root["id"]
            stories += related_ids(root, CHILD)
        elif kind == "User Story":
            stories.append(root["id"])
        else:
            sys.exit(f"Root {root['id']} is a {kind}; use an Epic or User Story.")
    items = ado.get_items(stories)
    frontier = [c for s in items.values() for c in related_ids(s, CHILD)]
    while frontier:
        fetched = ado.get_items(frontier)
        items.update(fetched)
        frontier = [c for i in fetched.values() for c in related_ids(i, CHILD) if c not in items]
    tests = ado.get_items({t for i in items.values() for t in related_ids(i, TESTED_BY)})

    def base(kind, item):
        f = item["fields"]
        node = {"key": f"{PREFIX[kind]}-{item['id']}", "id": item["id"], "rev": item["rev"],
                "title": f.get("System.Title", "")}
        for prop, field in TEXT_FIELDS.items():
            if prop != "title" and f.get(field):
                node[prop] = html_to_text(f[field])
        doc["ado"].setdefault("areaPath", f.get("System.AreaPath"))
        doc["ado"].setdefault("iterationPath", f.get("System.IterationPath"))
        return node

    seen_tests = set()
    for story_id in stories:
        story_item = items.get(story_id)
        if not story_item or story_item["fields"]["System.WorkItemType"] != "User Story":
            continue
        story = base("story", story_item)
        parent = related_ids(story_item, PARENT)
        if parent and parent[0] != doc["ado"].get("epicId"):
            story["parentId"] = parent[0]
        story["systemRequirements"], story["testCases"] = [], []
        covered_here = {story_id}
        for sys_id in related_ids(story_item, CHILD):
            sys_item = items.get(sys_id)
            if not sys_item or sys_item["fields"]["System.WorkItemType"] != "System Requirement":
                continue
            sys_node = base("sys", sys_item)
            sys_node["goLiveBlocker"] = bool(sys_item["fields"].get(GO_LIVE_FIELD))
            sys_node["softwareRequirements"] = [
                base("sw", items[sw_id]) for sw_id in related_ids(sys_item, CHILD)
                if sw_id in items and items[sw_id]["fields"]["System.WorkItemType"] == "Software Requirement"]
            covered_here |= {sys_id} | {sw["id"] for sw in sys_node["softwareRequirements"]}
            story["systemRequirements"].append(sys_node)
        for test_id, test_item in sorted(tests.items()):
            covers = set(related_ids(test_item, TESTS))
            if test_id in seen_tests or not covers & covered_here:
                continue
            seen_tests.add(test_id)
            node = base("test", test_item)
            node["steps"] = steps_from_xml(test_item["fields"].get(STEPS_FIELD))
            node["covers"] = sorted(covers & set(items))  # resolved to keys below
            node["attachments"] = [r["attributes"].get("name") for r in test_item.get("relations") or []
                                   if r["rel"] == "AttachedFile"]
            story["testCases"].append(node)
        doc["stories"].append(story)

    key_of = {node["id"]: node["key"] for _, node, _, _ in iter_nodes(doc)}
    for _, node, _, _ in iter_nodes(doc):
        if "covers" in node:
            node["covers"] = [key_of[i] for i in node["covers"] if i in key_of]
    Path(args.out).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    counts = {k: sum(1 for kind, *_ in iter_nodes(doc) if kind == k) for k in TYPES}
    print(f"Exported to {args.out}: " + ", ".join(f"{counts[k]} {TYPES[k]}" for k in TYPES))


# ---------------------------------------------------------------- plan / apply

def desired_ops(kind, node, current):
    """Return (ops, changes) to bring `current` (or a new item when None) in line with `node`."""
    fields = current["fields"] if current else {}
    ops, changes = [], []
    for prop, field in TEXT_FIELDS.items():
        if prop not in node:
            continue
        new = node[prop]
        old = fields.get(field, "")
        old_text = old if prop == "title" else html_to_text(old)
        if same_text(old_text, new):
            continue
        value = new if prop == "title" else text_to_html(new)
        ops.append({"op": "add", "path": f"/fields/{field}", "value": value})
        warn = " (replaces rich formatting)" if current and is_rich(old) else ""
        changes.append((prop + warn, old_text, new))
    if kind == "sys":
        wanted = bool(node.get("goLiveBlocker", False))
        if not current or bool(fields.get(GO_LIVE_FIELD)) != wanted:
            ops.append({"op": "add", "path": f"/fields/{GO_LIVE_FIELD}", "value": wanted})
            changes.append(("goLiveBlocker", str(fields.get(GO_LIVE_FIELD)), str(wanted)))
    if kind == "test" and "steps" in node:
        old_steps = steps_from_xml(fields.get(STEPS_FIELD))
        if not same_steps(old_steps, node["steps"]):
            ops.append({"op": "add", "path": f"/fields/{STEPS_FIELD}", "value": steps_to_xml(node["steps"])})
            changes.append(("steps", f"{len(old_steps)} steps", f"{len(node['steps'])} steps"))
    for field, value in (node.get("fields") or {}).items():
        if fields.get(field) != value:
            ops.append({"op": "add", "path": f"/fields/{field}", "value": value})
            changes.append((field, str(fields.get(field, "")), str(value)))
    return ops, changes


def link_ops(ado, kind, node, parent_id, cover_ids, current):
    """Parent and coverage links. Reparents when the parent differs; never removes coverage."""
    ops, changes = [], []
    relations = (current or {}).get("relations") or []
    if parent_id:
        existing = [(n, r) for n, r in enumerate(relations) if r["rel"] == PARENT]
        if not any(r["url"].endswith(f"/{parent_id}") for _, r in existing):
            for n, _ in sorted(existing, reverse=True):
                ops.append({"op": "remove", "path": f"/relations/{n}"})
            ops.append({"op": "add", "path": "/relations/-", "value": {"rel": PARENT, "url": ado.item_url(parent_id)}})
            changes.append(("parent", ", ".join(r["url"].rsplit("/", 1)[1] for _, r in existing), str(parent_id)))
    have = set(related_ids(current, TESTS)) if current else set()
    for cover_id in cover_ids:
        if cover_id not in have:
            ops.append({"op": "add", "path": "/relations/-", "value": {"rel": TESTS, "url": ado.item_url(cover_id)}})
            changes.append(("tests", "", str(cover_id)))
    extra = have - set(cover_ids) if current and kind == "test" else set()
    if extra:
        changes.append(("tests (not removed)", ", ".join(map(str, sorted(extra))), "also linked in ADO"))
    return ops, changes


def build_plan(ado, doc, mapping):
    validate(doc)
    cfg = doc.get("ado", {})
    ids = {node_key(k, n): resolve_id(k, n, mapping) for k, n, _, _ in iter_nodes(doc)}
    current = ado.get_items([i for i in ids.values() if i])
    plan = []
    for kind, node, parent, story in iter_nodes(doc):
        key = node_key(kind, node)
        item_id = ids[key]
        cur = current.get(item_id) if item_id else None
        if item_id and not cur:
            plan.append({"key": key, "kind": kind, "action": "missing", "id": item_id})
            continue
        if kind == "story":
            parent_id = node.get("parentId") or cfg.get("epicId")
        elif kind == "test":
            parent_id = None
        else:
            parent_id = ids[node_key("story" if kind == "sys" else "sys", parent)]
        cover_keys = node.get("covers", []) if kind == "test" else []
        entry = {"key": key, "kind": kind, "node": node, "id": item_id, "parentKey": None if kind in ("story", "test")
                 else node_key("story" if kind == "sys" else "sys", parent), "parentId": parent_id,
                 "coverKeys": cover_keys, "current": cur}
        if cur and node.get("rev") and cur["rev"] != node["rev"]:
            entry["stale"] = f"ADO revision {cur['rev']} differs from exported revision {node['rev']}"
        field_ops, changes = desired_ops(kind, node, cur)
        entry["action"] = "update" if cur else "create"
        entry["fieldOps"], entry["changes"] = field_ops, changes
        if cur:
            cover_ids = [ids.get(k) for k in cover_keys]
            _, rel_changes = link_ops(ado, kind, node, parent_id, [c for c in cover_ids if c], cur)
            entry["changes"] += [c for c in rel_changes if not c[0].startswith("tests (not")]
            entry["info"] = [c for c in rel_changes if c[0].startswith("tests (not")]
        plan.append(entry)
    return plan, ids


def print_plan(plan):
    counts = {}
    for entry in plan:
        action = entry["action"]
        if action == "update" and not entry["changes"]:
            action = "unchanged"
        for label, old, _ in entry.get("info", []):
            print(f"NOTE    {entry['key']}: {label}: {old}")
        counts[action] = counts.get(action, 0) + 1
        if action == "missing":
            print(f"MISSING {entry['key']}: work item {entry['id']} not found or no access")
        elif action == "create":
            print(f"CREATE  {entry['key']} {TYPES[entry['kind']]}: {entry['node']['title']}")
        elif entry["changes"]:
            stale = f"  [STALE: {entry['stale']}]" if entry.get("stale") else ""
            print(f"UPDATE  {entry['key']} ({entry['id']}): {', '.join(c[0] for c in entry['changes'])}{stale}")
    print("Summary: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))


def write_review(plan, path):
    lines = ["# Requirements review", "", f"Generated {datetime.date.today():%Y-%m-%d}. Nothing in ADO has changed.", ""]
    for entry in plan:
        if entry["action"] == "missing":
            lines += [f"## {entry['key']}: missing in ADO ({entry['id']})", ""]
            continue
        node = entry["node"]
        label = f"{PREFIX[entry['kind']]} {entry['id'] or 'new'}: {node['title']}"
        if entry["action"] == "create":
            lines += [f"## {label} (new)", ""]
            for prop in (p for p in TEXT_FIELDS if p != "title" and node.get(p)):
                lines += [f"**{prop}:** {node[prop]}", ""]
            if node.get("covers"):
                lines += [f"**Covers:** {', '.join(node['covers'])}", ""]
            if node.get("steps"):
                lines += ["| Step | Action | Expected result |", "| --- | --- | --- |"]
                lines += [f"| {n} | {s.get('action', '')} | {s.get('expected', '')} |" for n, s in enumerate(node["steps"], 1)]
                lines += [""]
            if node.get("note"):
                lines += [f"> {node['note']}", ""]
            continue
        text_changes = [c for c in entry["changes"] if c[0].split(" ")[0] in TEXT_FIELDS]
        if not text_changes:
            continue
        lines += [f"## {label}", ""]
        for prop, old, new in text_changes:
            if prop.startswith("title"):
                lines += [f"*Title was:* {old}", ""]
            else:
                lines += [f"**{prop} now:** {old}", "", f"**{prop} proposed:** {new}", ""]
        if node.get("note"):
            lines += [f"> {node['note']}", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"Review written to {path}")


def plan_cmd(args):
    doc = json.loads(Path(args.file).read_text(encoding="utf-8"))
    cfg = doc.get("ado", {})
    ado = Ado(cfg["organization"], cfg["project"])
    plan, _ = build_plan(ado, doc, load_map(args.map))
    print_plan(plan)
    if args.review:
        write_review(plan, args.review)


def apply_cmd(args):
    doc = json.loads(Path(args.file).read_text(encoding="utf-8"))
    cfg = doc.get("ado", {})
    ado = Ado(cfg["organization"], cfg["project"])
    mapping = load_map(args.map)
    plan, ids = build_plan(ado, doc, mapping)
    if any(e["action"] == "missing" for e in plan):
        sys.exit("Some mapped work items no longer exist; fix the file or map first (run plan).")
    backup = Path(args.backup) if args.backup else None
    if backup:
        backup.mkdir(parents=True, exist_ok=True)
    created = updated = skipped = 0
    for entry in plan:
        key, kind, node, cur = entry["key"], entry["kind"], entry["node"], entry["current"]
        if entry.get("stale") and not args.force:
            print(f"SKIP {key}: {entry['stale']}")
            skipped += 1
            continue
        parent_id = entry["parentId"] or (ids.get(entry["parentKey"]) if entry["parentKey"] else None)
        cover_ids = [ids[k] for k in entry["coverKeys"] if ids.get(k)]
        if kind == "test" and len(cover_ids) != len(entry["coverKeys"]):
            print(f"SKIP {key}: a covered requirement was not created")
            skipped += 1
            continue
        rel_ops, _ = link_ops(ado, kind, node, parent_id, cover_ids, cur)
        ops = entry["fieldOps"] + rel_ops
        if entry["action"] == "create":
            ops = [{"op": "add", "path": "/fields/System.AreaPath", "value": cfg["areaPath"]},
                   {"op": "add", "path": "/fields/System.IterationPath", "value": cfg["iterationPath"]}] + ops
            item = ado.create(TYPES[kind], ops)
            ids[key] = item["id"]
            mapping[key] = item["id"]
            save_map(args.map, mapping)
            created += 1
            print(f"CREATED {key} -> {item['id']}")
            cur = item
        elif ops:
            if backup:
                (backup / f"{cur['id']}-before.json").write_text(json.dumps(cur, indent=1), encoding="utf-8")
            cur = ado.patch(cur["id"], [{"op": "test", "path": "/rev", "value": cur["rev"]}] + ops)
            updated += 1
            print(f"UPDATED {key} ({cur['id']}): {', '.join(c[0] for c in entry['changes'])}")
        for path in node.get("attachments", []):
            if not Path(path).exists():
                continue  # exported attachments are names only
            names = {r["attributes"].get("name") for r in cur.get("relations") or [] if r["rel"] == "AttachedFile"}
            if Path(path).name not in names:
                url = ado.upload(path)
                cur = ado.patch(cur["id"], [{"op": "add", "path": "/relations/-",
                                             "value": {"rel": "AttachedFile", "url": url, "attributes": {"name": Path(path).name}}}])
                print(f"ATTACHED {Path(path).name} to {key}")
    print(f"Created {created}, updated {updated}, skipped {skipped}.")
    verify(ado, doc, mapping | {k: v for k, v in ids.items() if v})


def verify(ado, doc, mapping):
    plan, _ = build_plan(ado, doc, mapping)
    bad = [e for e in plan if e["action"] != "update" or e["changes"]]
    for entry in bad:
        print(f"MISMATCH {entry['key']}: {entry['action']} {', '.join(c[0] for c in entry.get('changes', []))}")
    print(f"Verified {len(plan) - len(bad)} of {len(plan)} items match the file.")
    return not bad


def verify_cmd(args):
    doc = json.loads(Path(args.file).read_text(encoding="utf-8"))
    cfg = doc.get("ado", {})
    if not verify(Ado(cfg["organization"], cfg["project"]), doc, load_map(args.map)):
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("export")
    p.add_argument("--root", type=int, action="append", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--organization", default="kardium-inc")
    p.add_argument("--project", default="Business Application Engineering")
    p.set_defaults(func=export)
    for name, func in (("plan", plan_cmd), ("apply", apply_cmd), ("verify", verify_cmd)):
        p = sub.add_parser(name)
        p.add_argument("--file", required=True)
        p.add_argument("--map", help="JSON file mapping keys to created work item IDs (resumable)")
        if name == "plan":
            p.add_argument("--review", help="write a Now/Proposed markdown review")
        if name == "apply":
            p.add_argument("--backup", help="directory for each updated item's JSON before the change")
            p.add_argument("--force", action="store_true", help="update items changed in ADO since export")
        p.set_defaults(func=func)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
