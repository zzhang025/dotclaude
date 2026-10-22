---
name: ado-requirements
description: Write, rewrite and publish SDLC requirements in Azure DevOps (ADO) as User Stories, System Requirements, Software Requirements and Test Cases, in plain, testable language. Use this whenever the user wants requirements created from a requirements document, meeting notes, a spec or a folder of documents; wants existing ADO requirements cleaned up, simplified, de-jargoned or made clearer; mentions System Requirements, Software Requirements, acceptance criteria, traceability, Modern Requirements or Smart Docs; or asks to create, sync or update requirement work items in ADO, even if they don't say "requirements skill".
---

# ADO requirements

Turn source material into clear requirements and publish them to Azure DevOps as linked work items. The bar: a business reviewer can read each requirement once and know exactly what the system does, and a tester can read it and know what to check.

The most common failure is not missing requirements. It is requirements that sound rigorous but say nothing: "The system shall assess reporting-period inclusion from documented ownership evidence." Nobody can build or test that. The fix is to state the actual rule: which date, which invoices, what happens when data is missing.

## Reference files

Read these when you reach the step that needs them:

- `references/writing-guide.md`: the hierarchy levels, what goes at each level, writing rules and title rules. Read before drafting or rewriting anything.
- `references/examples.md`: real before/after rewrites that the user accepted, grouped by the problem each one fixes. Read before drafting, and match its style.
- `references/elicitation-questions.md`: questions to ask, grouped by topic. Read before asking the user anything.
- `references/ado-work-items.md`: Kardium's ADO structure (types, fields, links, states), the requirements-file format and how to run `scripts/ado_requirements.py`. Read before touching ADO.

## Workflow

### 1. Work out the starting point

- **New requirements from documents.** The user points at a document, several documents or a folder.
- **Clean up existing ADO requirements.** The user points at an Epic, a story or a Modern Requirements Smart Doc link.
- **Add to an existing set.** Both of the above: export what exists, then draft the new items alongside it.

If the user gives a Smart Doc URL, the work items behind it are what matter. Export them from the Epic or stories (step 2) rather than scraping the page. Ask for the Epic or story ID if it isn't obvious.

### 2. Gather and rank the sources

For documents, read all of them before drafting. For each one, note what it covers, its date and its authority: a signed-off requirements set, an email ruling, meeting notes or an old draft. Build a short **decision log** of every business rule you find, with who decided it and when. Later decisions replace earlier ones. When the business owner (for example Finance) has ruled on something, their ruling wins over the author's wording. Write the requirement to the ruling and add a note that says so.

For existing ADO items, export them first:

```bash
python ~/.agents/skills/ado-requirements/scripts/ado_requirements.py export --root <EpicOrStoryId> --out requirements.json
```

ADO can drift from local copies, because people edit work items directly and delete some. Unless the user says otherwise, treat ADO as the source of truth and mention any drift you notice.

### 3. Ask what the sources don't answer

Use `references/elicitation-questions.md`. Ask only questions the sources leave open, and ask them in one batch with a recommended answer for each. When a rule is genuinely undecided, don't invent one. Write what the system does until it is decided (usually "leave it unresolved and say why") and record the open decision.

### 4. Draft in a local file

Write a requirements JSON file in the format given in `references/ado-work-items.md`. Keep it under the project's working area, for example `output/ado/<topic>/requirements.json`. Follow the writing guide and examples. Put a `note` on any item whose wording comes from a ruling, a later decision or a judgement call. Leave requirements that are already clear alone, because unnecessary churn costs reviewers time.

### 5. Show a few examples first

Before producing the whole set, show the user 4 to 6 representative before/after pairs (or new drafts) in the chat. Include at least one that a ruling changed. The user may want to adjust the style, and it is much cheaper to learn that on six items than on a hundred. Ask any blocking questions in the same message.

### 6. Produce the full review

Generate the review file and list it for the user:

```bash
python ~/.agents/skills/ado-requirements/scripts/ado_requirements.py plan --file requirements.json --review review.md
```

`plan` is read-only. It reports what would be created or updated, and flags any item edited in ADO since the export. Summarize the counts, the notes and anything that needs a decision.

### 7. Publish after explicit approval

Writing to ADO changes a shared system, so get a clear "yes" for this specific set first. Then run:

```bash
python ~/.agents/skills/ado-requirements/scripts/ado_requirements.py apply --file requirements.json --map map.json --backup backup/
```

- `--map` records key-to-ID for newly created items, so a rerun resumes instead of creating duplicates.
- `--backup` saves each item's previous JSON.
- Items changed in ADO since export are skipped. Re-export and merge rather than using `--force`, unless the user says to overwrite.
- `apply` verifies every item at the end. Report the verification result, the new IDs and anything skipped.

The script never deletes work items. If something should go, tell the user which items and let them remove them, or set the state to Obsolete if they ask.

### 8. Close out

Tell the user:
- what changed in ADO, with counts;
- where the review, map and backups are;
- which open decisions remain;
- any code or process gaps you noticed, such as behaviour the requirements now describe that the software doesn't do yet.

If local requirement documents should be updated from ADO, offer it as a separate step.
