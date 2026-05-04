---
name: write-a-prd
description: Write a Product Requirements Document (PRD) and file it as a GitHub issue. Use when the user wants to plan a feature, create a PRD, write requirements, or prepare a spec before implementation.
---

# Write a PRD

Produces a GitHub issue PRD that /tdd can execute against. Uses grill-me style interviewing to reach shared understanding before writing.

## Steps

You may skip steps if clearly unnecessary.

### 1. Problem Discovery

Ask the user for a long, detailed description of:
- The problem they want to solve
- Any potential ideas for solutions

### 2. Explore the Codebase

Verify the user's assertions and understand current state. Look for:
- Existing modules relevant to the feature
- Patterns already established
- Anything that contradicts or confirms the user's description

### 3. Relentless Interview

Interview the user about every aspect of the plan until you reach shared understanding. Walk down each branch of the decision tree, resolving dependencies one-by-one. Ask one question at a time. Provide your recommended answer with each question.

### 4. Module Sketch

Identify the major modules to build or modify. Actively look for **deep modules**: simple, stable interfaces that hide significant internal complexity and can be tested in isolation.

Present the module sketch to the user and confirm:
- Do these modules match your expectations?
- Which modules do you want tests written for, and at what boundary?

### 5. Write & File the PRD

Ask the user which GitHub repo to file the issue in. Default suggestion: the current repo (detected via `gh repo view`).

Write the PRD using [prd-template.md](prd-template.md) and file it via `gh issue create --repo <owner>/<repo>`. Share the issue URL when done.
