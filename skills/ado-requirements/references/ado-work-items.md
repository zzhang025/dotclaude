# ADO work items

## Kardium defaults

Verified against the live project in October 2026. Confirm them for a new project; other projects may use a different process template.

| Item | Value |
| --- | --- |
| Organization | `kardium-inc` (https://dev.azure.com/kardium-inc) |
| Project | `Business Application Engineering` |
| Hierarchy | Epic > User Story > System Requirement > Software Requirement |
| Tests | Test Case, linked to each covered User Story, System Requirement and Software Requirement |
| States | Draft, Under Review, Approved, Obsolete. New items start in Draft. |
| Example Epic | 17744 "Financial Inventory Reconcilliation" (area `Business Application Engineering`, iteration `Business Application Engineering\Financial Inventory Reconciliation`) |
| Reading view | Modern Requirements Smart Docs (the `smart-doc-hub` URL). Reviewers often read and edit there; the underlying data is the work items. |

### Fields

| Type | Required | Fields used for requirements text |
| --- | --- | --- |
| Epic | Title, State, Area, Iteration, Priority | |
| User Story | Title, State, Area, Iteration | Description (the "As a ... I need ... so that ..." text). Acceptance Criteria (usually left empty; see below). |
| System Requirement | Title, State, Area, Iteration, **Go Live Blocker** (`Custom.GoLiveBlocker`, boolean) | Description (the "shall" text). Acceptance Criteria holds the story criterion that this SYS satisfies. |
| Software Requirement | Title, State, Area, Iteration | Description (the "shall" text). **Solution Design** (`Custom.SolutionDesign`) holds algorithm detail such as patterns, keys and tie-breaks. |
| Test Case | Title, State, Area, Iteration | Description (coverage and setup). Steps (`Microsoft.VSTS.TCM.Steps`, XML). Attachments for fixtures. |

Other custom fields exist, for example Business Analyst, Business Process Owner, Business Justification, Primary Consultant and the substate fields. Set them through a node's `fields` map only when the user asks.

### Links

| Link | Reference name | Set on |
| --- | --- | --- |
| Parent | `System.LinkTypes.Hierarchy-Reverse` | The child, pointing to its parent (Story to Epic, SYS to Story, SW to SYS) |
| Tests | `Microsoft.VSTS.Common.TestedBy-Reverse` | The Test Case, pointing to each requirement it covers. The requirement then shows "Tested By". |
| Related | `System.LinkTypes.Related` | Optional, between related stories |

Descriptions are HTML. The script stores plain text in the file and converts it: blank-line-separated paragraphs become `<p>` and lines starting with `- ` become a bulleted list. If an existing description has a table or image and its text changes, the plan says so, because the rewrite replaces that formatting.

## Requirements file format

One JSON file per Epic or topic. Keys are your local IDs. Existing items carry their ADO `id` and the `rev` captured at export. New items have only a `key`.

```json
{
  "ado": {
    "organization": "kardium-inc",
    "project": "Business Application Engineering",
    "epicId": 17744,
    "areaPath": "Business Application Engineering",
    "iterationPath": "Business Application Engineering\\Financial Inventory Reconciliation"
  },
  "stories": [
    {
      "key": "US-008",
      "title": "Establish reporting-currency costs and period eligibility",
      "description": "As a Finance reviewer, I need reviewed costs expressed in CAD ..., so that ...",
      "systemRequirements": [
        {
          "key": "SYS-031",
          "title": "Convert invoice amounts to CAD",
          "description": "The system shall convert non-CAD invoice amounts to CAD using ...",
          "acceptanceCriteria": "Currency conversion shows the source amount, the rate and its date ...",
          "goLiveBlocker": false,
          "note": "Finance ruling (Garrett, 17 Sep): ECB is the approved source.",
          "softwareRequirements": [
            {
              "key": "SW-056",
              "title": "Convert invoice amounts using stored rates",
              "description": "Invoice Review shall convert invoice amounts to CAD using ...",
              "solutionDesign": "Optional algorithm detail for developers."
            }
          ]
        }
      ],
      "testCases": [
        {
          "key": "TC-008-01",
          "title": "Convert costs using the invoice-date rate",
          "description": "Coverage and setup notes. Upload fixtures from the attached zip.",
          "covers": ["US-008", "SYS-031", "SW-056"],
          "steps": [
            {"action": "Upload usd-weekend.pdf, dated August 2.", "expected": "The line uses the latest earlier ECB rate and shows that rate's date."}
          ],
          "attachments": ["testing/US-008/usd-weekend.pdf"]
        }
      ]
    }
  ]
}
```

Properties:

- `story.parentId` overrides `ado.epicId` for that story.
- `note` is review-only and is never written to ADO.
- `fields` (on any node) is a map of extra field reference names to values, written as they are.
- `attachments` are local file paths. Exported files list attachment names only; those are skipped.
- `covers` must list keys present in the file. Moving a node to a different parent in the file reparents it in ADO.

The script never deletes work items or removes test coverage links. It reports coverage links in ADO that the file doesn't list.

## Running the script

`scripts/ado_requirements.py` uses the standard library only. It authenticates with `az account get-access-token`, so run `az login` first, or set the `ADO_PAT` environment variable to a personal access token.

| Command | What it does | Writes to ADO? |
| --- | --- | --- |
| `export --root <id> [--root <id>] --out FILE` | Exports an Epic's or story's whole tree, including linked test cases | No |
| `plan --file FILE [--map MAP] [--review OUT.md]` | Lists creates, updates, reparenting and stale items; writes a Now/Proposed review | No |
| `apply --file FILE --map MAP --backup DIR [--force]` | Creates and updates items, records new IDs in MAP, backs up changed items, then verifies | **Yes** |
| `verify --file FILE [--map MAP]` | Confirms ADO matches the file | No |

Safety features in `apply`:
- It skips an item whose ADO revision differs from the `rev` in the file, because someone edited it after the export. Re-export, merge and plan again. Use `--force` only when the user says to overwrite.
- Each update includes a revision test, so a concurrent edit makes that one update fail instead of overwriting.
- It saves the map after every creation, so a rerun after a failure resumes without duplicates. Always pass `--map` when creating.
- Story, SYS and SW items are created before test cases, so coverage links can resolve.

Typical flows:

- **Rewrite an existing set:** `export`, edit the `title`/`description` and add `note`s, `plan --review`, show the user, `apply`.
- **New set from documents:** write the file with keys only, `plan --review`, show the user, `apply --map`, then commit or keep the map with the file.
- **Add stories to an existing Epic:** `export` the Epic, append the new stories with keys only, then `plan` and `apply --map`. Existing items show as unchanged.

## After publishing

- New work items may not appear in a Modern Requirements Smart Doc automatically. Ask the user whether the Smart Doc picks them up from the Epic or needs them added in the Smart Docs editor.
- Give the user the new IDs and links: `https://dev.azure.com/<org>/<project>/_workitems/edit/<id>`.
- Keep the requirements file, map, review and backups in the project's output area so later updates can be planned against them.
