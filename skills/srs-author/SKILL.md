---
name: srs-author
description: >
  Use this skill whenever the user wants to author, draft, generate, or review Software Requirements
  Specifications (SRS) from system-level requirements (SyRS) or user stories — especially when working
  with Azure DevOps (ADO) work items. Trigger on phrases like "write SRS", "draft software requirements",
  "create requirements from SyRS", "help me with SRS", "author requirements for [module]", or any time
  the user mentions deriving SRS from a CSV export, an ADO query, or a list of SyRS/user stories.
  Also trigger when the user uploads a CSV that looks like an ADO work item export and asks for help
  with requirements. This skill knows how to pull data directly from ADO via the az CLI and fall back
  to CSV upload, so always use it rather than trying to handle SRS authoring ad-hoc.
---

# SRS Authoring Skill

You are helping the user author **Software Requirements Specifications (SRS)** — the software-level
requirements derived from system requirements (SyRS) and user stories (US), typically destined for
import into Azure DevOps.

**Full worked example and house-style guide:** `references/ncm-example.md` — read it when you need
deep detail on phrasing, granularity, split patterns, or want a concrete before/after reference.
The glossary and lifecycle phases in that file are NCM-specific; adapt them for other modules.

---

## Step 1 — Get the source data

### Try az CLI first

Check whether `az` is available and configured:

```bash
az account show --query name -o tsv 2>/dev/null || echo "NOT_CONFIGURED"
```

If configured, ask the user which ADO organization and project to use — don't assume one. Then set
defaults so you don't repeat flags on every call:

```bash
az devops configure --defaults \
  organization=https://dev.azure.com/<org> \
  project="<project>"
```

#### Browse and select a query

List the top-level query folders, then let the user drill down:

```bash
# List root-level query folders/queries
az boards query list --depth 1 2>/dev/null

# Drill into a folder by path (use the 'path' value from the previous output)
az boards query list --path "Shared Queries/PI3 Software Releases" --depth 2
```

Present the tree to the user and ask which query to run. Queries have an `id` (GUID) field — use it.

#### Run the query — check flat vs. tree first

`az boards query --id <query-guid>` and `az boards query --wiql "..."` **only support flat
queries.** A US → SyRS → SRS query is normally a tree query (`WorkItemLinks`, mode `Recursive` or
`ReturnMatchingChildren`) — the exact shape you'll hit most often here. Against a tree query, these
commands don't error, they just return **empty output**, which reads like "no results" rather than
"wrong tool for this query." Try the simple form first, but if it comes back empty, don't conclude
there's no data — go to the REST fallback below instead of retrying variations of the same command.

```bash
az boards query --id <query-guid> --output json
```

If empty, fetch the query definition with its WIQL expanded, then POST that WIQL to the `wiql`
endpoint directly (GET isn't supported there):

```bash
# 1. Get the raw WIQL text for the saved query
az devops invoke --area wit --resource queries \
  --route-parameters project="<project>" query="<query-guid>" \
  --query-parameters '$expand=wiql' --api-version 7.1 --output json
# -> read the ".wiql" field from the response

# 2. POST that WIQL to the wiql endpoint (write {"query": "<wiql text>"} to a temp file first)
az devops invoke --area wit --resource wiql \
  --route-parameters project="<project>" \
  --api-version 7.1 --http-method POST --in-file wiql-body.json --output json
```

A tree query's response carries a `workItemRelations` array (source/target ID pairs) instead of a
flat `workItems` array — collect the unique `target` IDs from it as your work item list.

#### Fetch full details in batch

Once you have the IDs, batch-fetch full details via `workitemsbatch` rather than trusting the saved
query's own display columns — those are usually a narrow view (e.g. just Id/Type/Title/AssignedTo/
State/Tags/Software Release) and won't carry what authoring actually needs. Ask for the fields
explicitly:

```bash
# ids-and-fields.json: {"ids": [5907, 5908, ...], "fields": ["System.Id","System.WorkItemType",
#   "System.Title","System.Parent","System.AreaPath","System.IterationPath","System.State",
#   "System.Tags","System.Description","Custom.SoftwareRelease","Microsoft.VSTS.Common.Priority",
#   "System.AssignedTo"]}
az devops invoke --area wit --resource workitemsbatch \
  --route-parameters project="<project>" \
  --api-version 7.1 --http-method POST --in-file ids-and-fields.json --output json
```

For large result sets, page through IDs and build a local JSON/CSV. Use `jq` or a short Python
script to reshape if helpful.

#### Reconstruct the hierarchy

Work items from ADO don't come pre-nested. Reconstruct US → SyRS → SRS hierarchy by matching each
item's `System.Parent` field to another item's `System.Id` from the batch-fetched details — this is
more reliable than walking `workItemRelations` pairs directly, since `System.Parent` lives on the
item itself once fetched.

#### Confirm existing SRS are actually in scope

Step 3's "Already Covered" check only works if existing Software Requirement items are present in
this fetched set — not just the US/SyRS the original query targeted. Check `System.WorkItemType`
across the batch: if no SRS-type items appear at all, the query was scoped above the SRS level, and
every SyRS will look uncovered whether or not it actually is — a false "nothing exists yet" reading,
not evidence of a real gap.

Before trusting the coverage check, close that gap:

1. Collect the fetched SyRS IDs.
2. Run a supplementary WIQL query for SRS-type work items whose `System.Parent` is one of those
   SyRS IDs (or scoped by the same Area Path, if a parent-based WIQL isn't practical for the count
   involved).
3. Batch-fetch those results the same way as above and merge them into the working set before
   building the SyRS → SRS map in Step 3.

If you can't confirm SRS-type items are in scope and can't run the supplementary query, say so
explicitly in the output instead of presenting an "Already Covered" table that might be wrong.

### Fallback: CSV upload

If az is unavailable, not configured, or the user prefers it, ask them to export from ADO:
*Boards → Queries → open the query → `…` menu → Export to CSV*

Once uploaded, detect columns from the header row. Identify level by which `Title N` column is
populated (`Title 1` = US, `Title 2` = SyRS, `Title 3` = SRS). Hierarchy is positional — each
SyRS belongs to the US directly above it; each SRS to its parent SyRS.

The same scope gap applies here: if the export's query only descends to SyRS, `Title 3` will never
be populated and every SyRS will read as uncovered. Ask the user to confirm the export includes
existing SRS — or re-export with a query that does — before trusting the coverage check.

---

## Step 2 — Before authoring, establish context

Ask (or check the source data) for:

1. **Module name** — e.g. NCM, BPM, Label Service. This becomes the `<Module>` token in every SRS title.
2. **Area Path** — authoritative for phase/area assignment. If absent from the data, ask before proceeding.
3. **Prior-release SRS** — if available, read them first to calibrate phrasing, granularity, and attested
   phase tokens. Ask for them if the user has them. See `references/ncm-example.md` §11 for why this matters.

---

## Step 3 — Author the SRS

Derive SRS from SyRS only — never invent one from a US that has no SyRS; flag it instead.
Full title/statement patterns, coverage split patterns, and worked before/after examples live in
`references/ncm-example.md` §4–10 — read it before authoring your first SRS of the session, then
work from the quick rules below for the rest.

**Quick rules:**
- **Title:** `<Module> <Phase> - <Action>` (drop the phase for cross-phase behaviors like audit
  trails). Phase token (*when*) and Area Path (*who owns it*) are separate axes — don't force one
  to match the other.
- **Statement:** *"In the `<phase>` of the `<module>`, the system shall `<action>` so that `<outcome>`."*
  Atomic, testable, references the concrete system/store (e.g. "…in UniPoint").
- **IDs:** never invent numeric IDs — use `SRS-NEW-001`, `SRS-NEW-002`, … placeholders.
- **Coverage:** ~1 SRS per SyRS by default; 2–3 when a SyRS bundles distinct behaviors (split
  patterns in reference §6).
- **Existing SRS:** before authoring, map SyRS → existing SRS children via ADO's `System.Parent`
  (not a prior draft doc — ADO is the source of truth) — but only after confirming SRS-type items
  are actually in your fetched data (Step 1's "Confirm existing SRS are actually in scope"); a
  query scoped above the SRS level will make everything look uncovered. A SyRS with an existing
  SRS child is covered; if the SyRS description reveals a genuine uncovered behavior, add a
  *supplemental* SRS and say so in its Notes. List fully-covered SyRS in an "Already Covered"
  table. Full walkthrough and example in reference §6.
- **Allocation:** software only — park hardware/manual-process aspects under "Not allocated to
  software" with a one-line reason.
- **Open Questions/TBD:** flag vague or non-software SyRS as Open Questions; mark unspecified
  detail `[TBD]`; missing Area Path is the first open question. Obsolete-state SyRS get a one-line
  callout, not a full Open Question — unless a still-Draft SyRS looks like its near-duplicate.

---

## Step 4 — Output

Produce, in order: (1) per-SRS entries in the format from reference §9, (2) CSV rows mirroring the
input's exact column schema so they paste back into ADO, (3) a traceability summary table
(`SRS ID | SyRS parent | US | Title | Phase | Area Path`), (4) "Not allocated to software" section,
(5) Open Questions/TBDs section. Keep it inline/Markdown unless the user asks for a Word or CSV
file.

**Re-import note:** if the export has no parent-ID column, ADO nesting on import relies on row
position — place each SRS row directly beneath its SyRS parent.

---

## Quick checklist

- [ ] Columns/fields detected; US → SyRS → SRS hierarchy mapped
- [ ] Area Path present? If not, asked for it
- [ ] Prior-release example reviewed (or requested)
- [ ] Confirmed SRS-type items are actually in the fetched/exported data before trusting coverage
- [ ] Existing SRS checked against ADO's `System.Parent` links (not just a prior draft doc) —
      "Already Covered" table built; supplements added only for genuinely uncovered behavior
- [ ] Each SRS atomic, testable, "shall", correct title pattern; phase token vs Area Path kept distinct
- [ ] Software-only allocation; non-software parked with reasons
- [ ] Every SRS traced to SyRS → US; placeholder IDs only
- [ ] [TBD]s and Open Questions captured; US-without-SyRS flagged; Obsolete-state SyRS parked, not authored or over-flagged
- [ ] Output mirrors input columns; traceability summary included
