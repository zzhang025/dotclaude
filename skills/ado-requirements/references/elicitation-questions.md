# Questions to ask

Read the sources first and ask only what they leave open. Ask in one batch, number the questions, and give a recommended answer for each so the user can reply "yes to all but 4". Ask the blocking questions (sources, authority, ADO placement) first if you can't draft without them.

When the user doesn't know an answer, don't invent one. Record it as an open decision with an owner, and write what the system does until it is decided.

## Sources and authority

1. Which documents are in scope, and which one wins when they disagree?
2. Who has final say on business rules (for example, Finance on valuation, Quality on traceability)? Are there rulings in emails or meetings that aren't in the documents?
3. Are there decisions made since the documents were written? Is there an open-decisions list?
4. Is ADO or a local document the source of truth? If ADO already has items, should we update them or create new ones?
5. Are there earlier requirement sets, legacy apps or reference systems whose behaviour we must match or deliberately change?

## Scope and users

6. Who uses this? Name the roles (for example Reader, Reviewer, Administrator) and what each may do.
7. What is explicitly out of scope?
8. Which other systems does it read from or write to? Is any of them read-only (for example, the ERP)?
9. Does it touch regulated data or processes? Does traceability need to meet an audit standard?

## For each need (one story)

10. What triggers this? Who starts it, and from where?
11. What does the user do, step by step, and what do they get at the end?
12. Why does it matter? What goes wrong today without it? This becomes the "so that" clause.
13. How will we know it's done? List the acceptance criteria in the user's words.

## Business rules

These are the questions vague requirements usually skip. Get the actual rule.

14. Calculations: what formula, precision, rounding (which direction at the half) and currency? Which date is used: invoice, ship, receipt or posting date?
15. Sources of data: which source wins when two disagree (invoice, PO or receipt)? What counts as a match?
16. Defaults: what is the default for each category or option, and who may override it? Does an override need a reason?
17. Tolerances and limits: is any difference acceptable, and if so how much? What are the maximum file sizes, counts and date ranges?
18. Missing or bad data: is it blocked, flagged as a warning or left unresolved? Must unknown be kept distinct from zero?
19. Exceptions: duplicates, credits, returns, partial shipments, replacements. What happens to each?
20. Approval: what must pass before approval? Can a person override a failed check, and what is recorded when they do?

## Data, history and records

21. Which fields are required, and which are optional? What are the identifier formats (leading zeros, revisions)?
22. What must be recorded for each change: who, when, why, and the values before and after?
23. What happens to approved records when inputs change later: a new version, or reopened for review?
24. Who may delete what? What survives a deletion?
25. Retention, backups and restore expectations.

## Failure and concurrency

26. What if an external system is down or returns partial data?
27. What if two people edit the same item, or a batch partly fails?
28. What must survive a restart?

## Non-functional

29. Where does it run? How do users sign in?
30. Expected volumes and response times. How many users, invoices per month, rows in a grid?
31. Export formats and their consumers (for example Excel, or a downstream report owner).

## Testing and acceptance

32. Who signs off each story?
33. What test data can we use? Are real records allowed, or synthetic only? Does anything cost money to run (for example paid AI extraction)?
34. Manual acceptance tests, automated tests, or both? Do tests need attached fixtures?

## ADO placement

35. Organization, project and parent Epic (ID or name).
36. Area path and iteration path for new items.
37. State for new items (usually Draft). Must any custom fields be set (for example Go Live Blocker, Business Analyst, Business Process Owner)?
38. Should the items appear in a Modern Requirements Smart Doc? Which one, and who adds them?
39. Should test cases be created now, and should fixtures be attached?
40. A naming convention for local keys (US-001, SYS-001, SW-001, TC-001)? Should local documents be updated after ADO is published?
