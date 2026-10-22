# Writing guide

## The four levels

Each level answers a different question for a different reader. Mixing them up is the source of most bloat.

| Level | Answers | Form | Example |
| --- | --- | --- | --- |
| User Story | Who needs what, and why? | "As a <role>, I need <capability>, so that <benefit>." | As a Finance reviewer, I need reviewed costs expressed in CAD and assigned to the correct reporting period, so that reported amounts use an explainable exchange rate and ownership date. |
| System Requirement (SYS) | What must any solution do? | "The system shall ..." Names no product, screen or button, but states the rules, data and limits. | The system shall convert non-CAD invoice amounts to CAD using the ECB rate for the invoice date, or the most recent earlier rate if none was published that day. |
| Software Requirement (SW) | What does our chosen application do? | "<Application> shall ..." Names screens, buttons, statuses, file types and labels. | Settings shall have an Administrator-only action that downloads ECB rates for a chosen date range. |
| Test Case | How do we show it works? | Numbered steps, each with an action and an expected result. | 1. Upload usd-weekend.pdf, dated August 2. Expected: the line uses the latest earlier ECB rate and shows that rate's date. |

Typical shape: each story has 3 to 5 SYS, each SYS has 1 to 3 SW, and each story has 1 to 3 test cases covering its SW. One SYS usually maps to one acceptance criterion of the story. In Kardium's ADO the criterion text is stored on the System Requirement (see `ado-work-items.md`).

A system requirement can be concrete. "Solution-independent" means it doesn't name the product or its screens. It does not mean it should be vague. Rules, numbers, dates, defaults and failure behaviour all belong at the SYS level.

Algorithm detail that a business reviewer doesn't need, such as a PO-number regex, name-matching keys or tie-break order, goes in the Software Requirement's **Solution Design** field, not its description.

## Rules

1. **State the rule, not that a rule exists.** "Consistently with the applicable rounding policy" tells the reader nothing. "Round each CAD line to the cent, halves away from zero" does. If you write "policy", "rules", "criteria" or "approved", ask what the policy is and write that instead.

2. **If the rule is undecided, say what happens meanwhile.** For example: "Until Finance decides which exchange rate applies to credits, the credit's CAD cost shall stay incomplete." Name the open decision in a note, not in the requirement text.

3. **Name concrete things.** Write reviewer, Administrator, invoice line, PO line, receipt, CAD, ECB, ship date, Excel file. Avoid these abstractions, which hide meaning: evidence, evidenced, basis, aspect, identifiable, outcome, disposition, population, eligibility, treatment, interpretation, relationship, guarantees, capacity, artefact, scope. Each one usually stands in for a specific noun. Find it.

4. **Use plain verbs.** Write "keep" not "retain" or "preserve", "show" not "present" or "surface", "check" not "validate" or "assess", "decide" or "mark" not "establish" or "determine", "use" not "utilize" or "apply", and "say why" or "show the message ..." not "explain".

5. **One idea per sentence.** Split semicolon chains. If a sentence has more than one "and ... while ... without ...", break it up. Aim for under about 30 words.

6. **Spell out condition lists.** "Only for an active unprotected goods line with automatic selection enabled" packs four conditions into adjectives. Write "only when all of these are true: ...; ...; ...". Do the same for lists of checks.

7. **Define jargon where it's used, or drop it.** Terms like "unprotected line", "normalization" or "capacity" mean something to the developer and nothing to the reviewer. Say what they mean.

8. **Make it testable.** A tester should be able to read the requirement and know what to look for: status names, labels, limits, rounding, what appears on screen, and what must not change. If you can't picture the test, the requirement is too vague.

9. **Say what happens when data is missing or wrong.** Unknown is not zero. State whether the item is blocked, flagged or left unresolved, and what the user sees.

10. **Use active voice with a named actor.** "The system shall", "Invoice Review shall", "the reviewer may". Avoid "is retained", "shall be identified" and similar passives where it's unclear who does what.

11. **Make cross-references self-contained.** Don't write "the field set below", which disappears when the item is moved, or "the common guarantees", which nobody can look up. Name the other requirement by title and ADO ID, or state the rule inline.

12. **Avoid words that mean something else to the reader.** "General ledger" means the accounting GL to Finance. "Receipt" can mean a goods receipt or a payment receipt. Choose a word that doesn't collide.

13. **Don't describe implementation that isn't true.** "Backed up on a configured schedule" was wrong when Azure SQL manages the schedule. Describe the behaviour the user relies on.

14. **Keep requirements current with decisions.** When a later decision or a business-owner ruling changes behaviour, rewrite the requirement to match. Add a note naming who decided, when and where it is recorded. When a ruling conflicts with the user's preferred wording, follow the ruling and say so plainly in the note.

15. **Leave clear requirements alone.** If a requirement is already plain and testable, don't reword it for the sake of it. Fixing a typo or broken punctuation is fine.

16. **Punctuation.** No em dashes; use a period or a comma. Use straight quotes. Use colons only before a list.

## Titles

A title is what people scan in backlogs and Smart Docs, so it should say what happens.

- Start with a verb, use plain words and keep it to about 8 words: "Convert invoice amounts to CAD", "Prevent over-allocating receipts", "Delete invoices by role".
- Don't use a nominalized abstraction: "Establish evidenced currency conversion", "Determine reporting-period eligibility", "Summarize complete finalized result sets".
- A SYS title and its SW titles can be close, but each SW title should name its own slice: "Convert invoice amounts using stored rates", "Flag invoices that cannot be converted".

## Notes

A note travels with the draft for the reviewer. It is not written into ADO unless the user asks. Use one of these labels:

- **Finance ruling** (or whichever business owner): a ruling overrides the current or requested wording. Say who, when, and what it overrides.
- **Decision**: brings the text in line with a later recorded decision. Give the date and the decision ID if there is one.
- **Code gap**: the software doesn't yet do what the requirement now says.
- **Please check**: a judgement call the reviewer should confirm.

## Self-check before showing the user

For each requirement, ask:
- Could a tester write a pass/fail check from this alone?
- Is there an abstract noun hiding a concrete one?
- Is there a rule referred to but not stated?
- Does it say what happens when data is missing?
- Would the business owner recognize their ruling in it?
