# SRS Authoring — Full House-Style Guide (NCM Reference)

This file is the **NCM (Non-Conformity Module) reference implementation** of the SRS authoring
framework. Use it as the style exemplar when working on NCM requirements, and as a detailed
pattern-library when authoring SRS for any other module. Where it says "NCM", substitute your module.

---

## 1. The requirements chain

```
US   (User / stakeholder requirements)
  ↓ refined into
SyRS (System requirements)
  ↓ allocated to software as
SRS  (Software requirements)   ← what you author
```

SRS derive from SyRS — never invent SRS directly from a US that has no SyRS (flag it, see §8).

---

## 2. Inputs and how to read them

* **Source CSV**, typically named `US__SyRS__SRS_-_<Module>_<version>.csv`.
* **Detect columns from the header row** — don't assume a fixed schema. Identify level by which
  `Title N` column is populated (`Title 1` = US, `Title 2` = SyRS, `Title 3` = SRS). Hierarchy is
  **positional**: each SyRS belongs to the US above it; each SRS to the SyRS above it.
* **Area Path** — authoritative signal for functional area. If missing, ask before assigning
  area/phase tokens. Don't guess.
* Column sets differ across releases — mirror whatever the input uses on output.

---

## 3. Authoring workflow

1. Read the CSV; detect columns; classify rows; map the positional hierarchy.
2. Check existing SRS — **don't duplicate**; only add what's missing.
3. For each SyRS not yet fully covered, derive the SRS needed to satisfy it.
4. Make each SRS **atomic, testable, verifiable**, in the title + "shall" format (§5, §9).
5. Allocate to **software only**; park hardware/operational/manual items (§7).
6. Trace each SRS to its SyRS parent ID (→ US where the chain exists).
7. Flag vague, contradictory, or non-software items as **Open Questions**; mark unspecified
   detail as `[TBD]` (§8).

---

## 4. IDs

* Real IDs in ADO are **numeric** (e.g. SRS `9882`, SyRS `7087`). **Never invent a numeric ID.**
* New items get temporary placeholders: `SRS-NEW-001`, `SRS-NEW-002`, …

---

## 5. Titles, statements, and the two axes

### SRS title pattern

```
<Module> <Phase> - <Action/Feature>
```

Example: *"NCM Origination - Write NC Number to Source Production Step"*

Use crisp, implementation-flavored action verbs: *Write, Create, Display, Block, Validate,
Disable, Associate, Capture, Add, Allow, Record, Verify, Return, Support, Print, Move, Split,
Assign, Notify, Restrict, Persist.*

### Two distinct axes — keep them separate

* **Phase token (in the title)** = the lifecycle phase the action occurs in (e.g. Origination,
  Segregation, Disposition, Closure). Describes *when* in the workflow.
* **Area Path (ADO field)** = the functional/team area (e.g. `…\NC Origination`,
  `…\Production Execution`). Describes *what part of the system owns it*.

> Example: an SRS filed under `…\Production Execution` area can still be titled
> `NCM Origination - …` because the action happens at origination.

Rules of thumb:
* Derive the phase token from the lifecycle phase the SyRS describes; confirm against Area Path.
* For genuinely **cross-phase** behaviors (traceability, audit trails spanning the lifecycle),
  drop the phase: `<Module> - <Action>`.
* Only use phase tokens that are **attested** for the module/release. Mark provisional tokens clearly.

### Requirement statements

Template:
> *"In the `<phase>` of the `<module>`, the system shall `<action>` so that `<outcome>`."*

Use **"shall"**, atomic, referencing the specific module/phase and the concrete system/store
(e.g. "…in UniPoint", "…in the Process Tracking Tables").

---

## 6. Coverage and granularity

* **Default to ~1 SRS per SyRS** — but the house norm legitimately produces **2–3 SRS per SyRS**
  when a SyRS bundles distinct behaviors. Common split patterns:
  * **Field-capture SyRS** → one SRS per field (Part Number, Description, Quantity, NC Type,
    Priority, PBO Number…).
  * **Authorization SyRS** → "verify certification/eligibility" + "block unauthorized users."
  * **Cancellation/confirmation SyRS** → "cancel button before confirmation" + "confirmation
    prompt" + "disable after confirmation."
  * **Identifier SyRS** → "create record with sequential ID" + "display assigned ID to user."
* If holding to a 1:1 ratio on request, note where the house norm would naturally split further.
* Don't add an SRS for a SyRS already covered; record it under "Already covered."

### When ADO has moved past a prior draft

An earlier SRS pass sometimes exists only as a draft document rather than as real ADO items. By the
time you're asked to pick the work back up, ADO may have absorbed *some* of that draft as formally
numbered Software Requirements — not all of it. Trust ADO's `System.Parent` links over the draft: a
SyRS with an existing SRS child is covered, full stop, even if the draft proposed a different framing
or a different SRS count for it.

Still, re-check the SyRS description against what the existing SRS actually states before assuming
full coverage — it's common for one SyRS to describe two behaviors when only one made it into the
imported SRS. Example from a Label Service pass: SyRS "Test environment for proof print trigger &
data sourcing" described both (a) not triggering production records, and (b) fetching source-system
data to populate the label. Only (a) had been imported as an SRS. The fix was a *supplemental* SRS
covering just (b), with its Notes stating plainly: "Supplements existing SRS 13304 — does not replace
it." That one line is what keeps a reviewer from mistaking it for an accidental duplicate.

---

## 7. Software-only allocation

* Allocate only the software behavior.
* Park hardware, physical-handling, and manual-process aspects under **"Not allocated to
  software"** with a one-line reason.
* Typical split: software *creates the move action / generates the print job / writes the record*;
  the *physical movement or printing* is operational/hardware.

---

## 8. Open Questions & TBD discipline

* Flag vague, contradictory, or non-software SyRS as **Open Questions** rather than guessing.
* Mark unspecified detail inline as `[TBD]` (e.g. status value sets, role definitions,
  configuration sources, audit field sets, block-vs-reassign behavior).
* **US with no SyRS** → flag; SRS can't be derived until a SyRS exists.
* If the export has **no parent-ID column**, state that links were traced positionally and ask
  for confirmation.
* If **Area Path is absent**, make it the first open question.
* **Obsolete-state SyRS** → don't author against them and don't list them as an Open Question by
  default; a one-line callout that it's obsolete is enough. Only escalate to a real Open Question
  if a still-Draft SyRS looks like a near-duplicate (same title/description) — then ask whether the
  obsolete item's intended behavior migrated to the live one or was dropped.

---

## 9. SRS entry format

> **SRS-NEW-001** — *`<Module> <Phase>` - `<Action>`*
> - **Statement:** In the `<phase>` of the `<module>`, the system shall `<action>` so that `<outcome>`.
> - **Traces to:** SyRS `<id>` → US `<id>`  ·  **Area Path:** `<path>` (or `[pending]`)
> - **Priority:** High / Medium / Low
> - **Acceptance criteria:** how it's verified
> - **Notes:** counterpart SRS, dependencies, established-vocabulary cross-refs, increment considerations

---

## 10. Output

* **Default:** a readable list of new SRS in the §9 format, **plus** the same rows formatted to
  match the **input CSV's columns** (mirror its exact schema) so they paste straight back into ADO.
  Use placeholder IDs; set `State` to match the export's working state.
* Always include a **traceability summary**: `SRS ID | SyRS parent | US | Title`; add `Phase`
  and `Area Path` columns when those axes are in play.
* List **Not allocated to software** and **Open Questions / TBDs** at the end.
* Keep it inline/Markdown unless a Word/PDF/file deliverable is requested.
* **Re-import note:** if the export has no parent-ID column, ADO nesting on import relies on row
  position — place each SRS row directly beneath its SyRS parent.

---

## 11. Calibrating to house style from a prior release

Before finalizing a new release's SRS, **review the SRS from a previous release of the same module**.
It reveals:
* The **real phrasing and granularity** of titles and "shall" statements.
* The **attested phase tokens** and **Area Path values** in use.
* **Established domain vocabulary** to reuse verbatim.
* Whether a class of SyRS is conventionally split into multiple SRS.

If you don't have a prior-release example, **ask for one**. When vocabulary has shifted between
releases, prefer the current SyRS wording and cross-reference the prior term in Notes.

---

## 12. NCM glossary & lifecycle phases

**Lifecycle phases (NCM):** Origination · Segregation · Disposition · Closure · (In-Process visibility)

*Confirm which phases are attested for the release via the Area Path / prior-release SRS.*

**Glossary:**
* **NCM** — Non-Conformity Module · **BPM** — Build Product Module
* **Origination** — the entry context in which an NC is raised
* **Segregation** — separating, statusing, locating, labeling, and holding nonconforming material
* **Parent NC** — the primary NC in a linked set · **TagNC** — a tagged child NC linked to a Parent NC
* **Process Tracking Tables** — where production operation step records live
* **UniPoint** — QC/NC record store (inspection records, NC records)
* **OData / ItemBatches** — data access layer; batch/procurement lineage (PO, vendor, vendor batch,
  manufacturer), including behavior after a batch split
* **PBO** — Purchase/Production Buy Order reference
* **ADO** — Azure DevOps (item tracking, by increment)

---

## 13. Quick checklist

* [ ] Columns detected from the header; levels and positional hierarchy mapped
* [ ] Area Path present? If not, asked for it
* [ ] Prior-release example reviewed for house style (or requested)
* [ ] Existing SRS checked against ADO parent links (not just a prior draft); supplements marked
      explicitly where they extend, not duplicate, an existing SRS
* [ ] Obsolete-state SyRS parked with a one-line callout, not authored or over-flagged
* [ ] Each SRS atomic, testable, "shall," correct `<Module> <Phase> - <Action>` title
* [ ] Phase token vs Area Path kept distinct; provisional tokens flagged
* [ ] Established vocabulary reused (Parent NC/TagNC, UniPoint, etc.)
* [ ] Software-only allocation; non-software parked with reasons
* [ ] Every SRS traced to SyRS → US; placeholder IDs only
* [ ] `[TBD]`s and Open Questions captured; US-without-SyRS flagged
* [ ] Output mirrors the input CSV columns; traceability summary included
