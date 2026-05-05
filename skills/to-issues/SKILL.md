---
name: to-issues
description: Use when the user wants to convert a plan, spec, or PRD into independently-grabbable issues on the project issue tracker. Triggers on requests to break down work into tickets, create implementation issues, or convert a PRD into a Kanban board.
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be **HITL** or **AFK**:
- **HITL** — requires human interaction (architectural decision, design review)
- **AFK** — can be implemented and merged without human interaction

Prefer AFK over HITL where possible.

**Vertical slice rules:**
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Detect the issue tracker

Before publishing, check whether a remote issue tracker is available:

- Run `git remote -v` to see if a GitHub/GitLab remote exists.
- If a GitHub remote is present, use it as the issue tracker (proceed as normal below).
- If **no remote is found**, fall back to a local `ISSUES.md` file (see Local Fallback below).

### 6. Publish the issues

#### Remote tracker (GitHub)

For each approved slice, publish a new issue. Apply the `needs-triage` label so each issue enters the normal triage flow.

Publish issues in **dependency order** (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

#### Local fallback (`ISSUES.md`)

If no remote tracker exists, write all issues to `ISSUES.md` in the project root. Append if the file already exists; create it if it doesn't.

Use this structure:

```markdown
# Issues

## [#N] <Title>

**Type:** HITL / AFK
**Status:** Open

### What to build

A concise description of this vertical slice.

### Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

### Blocked by

- #M <Title of blocking issue>, or "None - can start immediately"
```

Number issues sequentially, starting from 1 (or continuing from the highest existing `#N` in the file).

After writing, tell the user: "No remote issue tracker detected — issues written to `ISSUES.md`."

---

Use this issue body template for both remote and local:

```markdown
## Parent

A reference to the parent issue on the issue tracker (if the source was an existing issue, otherwise omit this section).

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- A reference to the blocking ticket (if any)

Or "None - can start immediately" if no blockers.
```

Do NOT close or modify any parent issue.