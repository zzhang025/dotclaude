# Before and after examples

Real rewrites from the Financial Inventory Reconciliation (Invoice Review) requirements, October 2026. The "Before" text was in ADO; the user accepted the "After" text and it was published. They are grouped by the main problem each one fixes. Most "Before" items have several problems.

Use these to calibrate style. Don't copy their business rules into other projects.

## 1. The rule is referred to but never stated

**SYS: Determine reporting-period eligibility → Assign invoices to a reporting period**

> Before: The system shall assess reporting-period inclusion from documented ownership evidence, identifying included, excluded and unresolved transactions.
>
> After: The system shall include in a reporting period every invoice dated within that period. It shall also include an invoice dated after the period end if its ship date and Incoterms show that Kardium owned the goods on the last day of the period. If the ship date or Incoterms are missing, or there is no ownership rule for that Incoterm, the system shall mark the invoice Unresolved.

The user had proposed "use the ship date, falling back to the invoice date". Finance had ruled otherwise (ownership by Incoterms and ship date; include all invoices dated in the period, then add later ones), so the ruling won and the note said so:

> Finance ruling (Sindhu and Garrett, 21 Sep): ownership on the last day of the period, decided by Incoterms and ship date, governs. This overrides the proposed "ship date first, then invoice date" wording. Which Incoterms give ownership on which date is still open (P07).

**SYS: Establish evidenced currency conversion → Convert invoice amounts to CAD**

> Before: The system shall establish each currency conversion from approved rate evidence and date-selection rules, explaining unavailable or unacceptable inputs.
>
> After: The system shall convert non-CAD invoice amounts to CAD using the ECB rate for the invoice date, or the most recent earlier rate if none was published that day. If no rate is available, the system shall show the CAD amount as unavailable and state why.

**SYS: Calculate traceable reporting-currency amounts → Round CAD amounts and keep the original amounts**

> Before: The system shall calculate reporting-currency amounts consistently with the applicable rounding policy while retaining original values and conversion evidence.
>
> After: The system shall round each CAD line amount to the cent, rounding halves away from zero. It shall keep the original invoice-currency amount and the rate used.

**SYS: Classify additional charges and set relationships → Decide which charges go into unit cost**

> Before: The system shall classify additional charges and set/component relationships using documented evidence and policy, distinguishing included, excluded and unresolved treatment.
>
> After: The system shall classify each additional charge on an invoice as included in unit cost, excluded or unresolved. Non-GST taxes (including PST), duties and tariffs shall be included by default. GST, freight, tooling, setup, engineering and certificates of conformance shall be excluded by default. A reviewer may override the default with a reason. A set price shall be split across its component parts only when the invoice or PO identifies the components.

## 2. Abstract nouns hiding concrete ones

**SYS: Propose selections while preserving reviewer decisions → Suggest PO lines without overriding the reviewer**

> Before: The system shall propose selections consistently while preserving reviewer work and distinguishing candidate discovery, eligibility and human approval.
>
> After: The system shall suggest a PO line for an invoice line only when exactly one PO line matches. A suggestion shall not replace a PO line the reviewer already selected, and shall not count as approval.

**SYS: Record explicit reconciliation decisions → Confirm, reject or reopen line decisions**

> Before: The system shall record explicit confirmation, rejection or reopening of identified reconciliation aspects only after their applicable current checks, with grouped actions completed in full or left unchanged.
>
> After: The system shall let a reviewer confirm, reject or reopen the PO match, unit conversion or receipt allocation on a line. Confirmation shall be allowed only if the checks pass at the time of saving. When several lines are saved together, either all are saved or none are.

**SYS: Summarize complete finalized result sets → Show totals for the filtered data**

> Before: The system shall provide complete-result counts and meaningful summaries that reconcile with their member records.
>
> After: The system shall show the row count and totals for all rows that match the current filter, not just the rows on screen. Group totals shall add up to the overall total.

**SW: Enforce organizational identity and permissions → Enforce sign-in and roles on every request**

> Before: Invoice Review shall use the identified organizational user and assigned permissions for viewing, correction, approval and configuration, enforcing restrictions on direct requests as well as screens. The actor recorded for an action shall come from that identity, not editable request text. Denied or unavailable authorization shall not grant access or change work.
>
> After: Invoice Review shall sign users in with their Kardium (Entra) account and use their assigned role. Readers can view. Reviewers can also correct and approve. Administrators can also change settings, maintain exchange rates and delete matched invoices. Invoice Review shall check the role on every server request, not only by hiding buttons. The user recorded on each action shall come from the sign-in, not from the request. If the role cannot be checked, access shall be denied.

## 3. Dense sentences and packed condition lists

**SW: Apply proposals without overwriting existing review work** (title kept)

> Before: Invoice Review shall initialize valid first proposals as unapproved data only when review work does not already exist. Later proposals shall remain separate until explicitly applied after current validation; replacement shall preserve earlier values/decisions and require renewed review. Outdated or failed application shall leave saved work unchanged.
>
> After: If an invoice has no review work yet, Invoice Review shall load extraction results as unapproved values. If review work exists, it shall hold new results separately until the reviewer applies them. Applying them shall keep the earlier values in history and reopen the affected lines for review. If applying fails, saved work shall not change.

**SW: Propose unique eligible PO line selections → Select a PO line automatically only when one matches**

> Before: Invoice Review shall propose a unique PO-line selection only for an active unprotected goods line with automatic selection enabled, no existing selection and exactly one candidate.
>
> After: Invoice Review shall select a PO line automatically only when all of these are true: automatic selection is turned on; the line is a goods line; the reviewer has not already selected a PO line, edited the line, or confirmed or rejected its match; and exactly one PO line matches.

**SW: Evaluate and record matching checks → Run and record each matching check**

> Before: Invoice Review shall separately check goods classification, nonempty distinct valid selections, candidate membership, part ambiguity, nonblank matching invoice/line currency and blocking source warnings.
>
> After: Invoice Review shall run each of these matching checks separately and report each result: the line is classified as goods; at least one PO line is selected and none is selected twice; each selected PO line is one of the matching candidates; the part number does not match more than one distinct part on the PO; the invoice and line currencies are present and the same; and no blocking extraction warning remains.

**SW: Compare line amounts under the recorded rounding policy → Check line amounts and the invoice total**

> Before: Invoice Review shall compare reconstructed and printed line amounts under the recorded rounding policy and retain the invoice-total check including separate charges. It shall show differences or incomplete comparisons without changing source values, substituting PO prices or adding balancing charges. Separate charges shall remain outside goods-only cost.
>
> After: Invoice Review shall accept a line when quantity x unit price / price basis, rounded to the cent with halves rounded away from zero, equals the printed line amount. It shall check that the goods and charge lines add up to the invoice total. It shall show any difference, and shall not change printed values, use PO prices or add a balancing charge to remove it. Charges shall not be included in the goods unit cost.

## 4. Stale text that contradicts a later decision

**SW: Flag missing or unacceptable conversion inputs → Flag invoices that cannot be converted**

> Before: Invoice Review shall identify missing currency/date, unavailable rate, unsupported currency or an unacceptable prior-rate age as incomplete conversion, never zero or assumed rate 1. It shall evaluate rate age under a recorded policy; if that policy is unavailable for a stale-rate decision, it shall report the unresolved condition rather than silently accept it.
>
> After: Invoice Review shall mark the CAD conversion incomplete when the invoice currency or date is missing, the currency is not supported, or there is no valid rate on or before the invoice date. A zero, negative or future-dated rate is not valid. Invoice Review shall not use a rate of zero or assume a rate of 1. A rate shall not be rejected because of its age.
>
> Note: Decision (25 Sep): no maximum rate age. The old text required a rate-age policy that had been dropped.

**SYS: Back up review data on schedule → Back up review data automatically**

> Before: The system shall automatically back up saved invoice-review data on a configured schedule.
>
> After: The system shall back up saved review data automatically.
>
> Note: Decision (26 Sep): Azure SQL manages the backup schedule, so there is no schedule to configure.

## 5. Broken references, broken sentences and colliding words

**SW: Apply saved-action guarantees to corrections and decisions → Apply the standard save rules to corrections and decisions**

> Before: Invoice Review shall apply the common saved-action guarantees to corrections and decisions, including actions from Finalized Data.
>
> After: Corrections and decisions, including those made from Finalized Data, shall follow the save rules in "Save attributable review history consistently" (18046): the user and time are recorded, the change saves completely or not at all, and a save from an out-of-date view is rejected.

**SW: Format self-contained sortable Excel tables → Format the export as sortable Excel tables**

> Before: Invoice Review shall produce Excel tables Quantities, prices and factors shall be numeric with saved precision retained; identifiers shall preserve leading zeros and full revisions as text.
>
> After: Invoice Review shall produce an Excel workbook of sortable tables. Quantities, prices and conversion factors shall be numeric cells, each with a text column holding the exact saved value, because Excel keeps only 15 significant digits. Part numbers, PO numbers and other identifiers shall be text, so that leading zeros and revisions are kept.

**SW: Preview and save evidenced normalization corrections** (title kept)

> Before: Invoice Review shall allow reasoned correction of quantity interpretation, price basis, conversion factor and target unit with source/conversion evidence, preview recalculation and cancel without saving. All changes are stored in a general ledger that can be replayed to regenerate a line in normalized table.
>
> After: Invoice Review shall let a reviewer correct the quantity, price basis, conversion factor or stock unit, citing where the correct value comes from, preview the recalculated values and cancel without saving. Every saved change shall be recorded in a line history that can be replayed to rebuild the line's current converted values.
>
> Note: Please check: "general ledger" replaced with "line history" to avoid confusion with the accounting GL.

## 6. Already good: left unchanged

These were already plain and testable, so they were not reworded:

- Invoice Review shall accept files containing 1–50 pages and measuring no more than 25 MiB each. A file exceeding either limit shall be rejected with a message identifying the exceeded limit, and shall not appear as an accepted invoice.
- Invoice Review shall allow the reviewer to select 1–50 invoice PDFs for one upload. If more than 50 files are selected, it shall explain the limit and start none of the uploads from that selection. The limit shall apply to each upload selection, not to the total number of invoices already held.
- Invoice Review shall start extraction only when the reviewer explicitly requests it. Upload completion, opening a PDF or preview, refreshing the page and restarting the application shall not start extraction.
- Invoice Review shall compare vendor ID first and allow name/alias fallback only when no ID is supplied.

These work because each one names concrete inputs, gives exact limits, says what the user sees on failure, and lists what must not trigger the behaviour.

## Title rewrites at a glance

| Before | After |
| --- | --- |
| Establish evidenced currency conversion | Convert invoice amounts to CAD |
| Determine reporting-period eligibility | Assign invoices to a reporting period |
| Associate identical copies with existing evidence | Recognize re-uploaded copies of the same file |
| Start invoice-detail processing on reviewer request | Extract invoice details only when a reviewer asks |
| Establish supplier and item compatibility | Match supplier and part numbers to the PO |
| Inspect complete purchasing evidence without changing work | View the full PO and its receipts |
| Validate compatible quantities and shared capacity | Prevent over-allocating receipts |
| Identify repeated invoice identities | Flag possible duplicate invoices |
| Validate and retain adjustment outcomes | Apply credit notes to the original invoice |
| Enforce role-dependent invoice deletion | Delete invoices by role |
| Preserve attributable history and consistent saves | Keep a change history and prevent lost updates |
