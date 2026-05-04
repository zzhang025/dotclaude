# Reference: Improve Codebase Architecture

## Dependency Categories

When classifying coupling between modules, assign one of these four categories:

| Category | Description | Example |
|---|---|---|
| **Same-layer** | Modules at the same abstraction level calling each other directly | Service A directly calls Service B |
| **Cross-layer** | Higher-level module reaching down past its direct dependency | Controller directly touching the DB |
| **External/infrastructure** | Module coupled to a specific framework, driver, or I/O mechanism | Business logic importing EF Core |
| **Circular** | Two modules mutually depend on each other | A → B and B → A |

Use the category to guide the interface design strategy:

- **Same-layer** → introduce a shared abstraction both sides depend on
- **Cross-layer** → add a layer; move the lower concern behind an interface
- **External/infrastructure** → apply ports & adapters; define a port the business logic uses and an adapter that wraps the framework
- **Circular** → break the cycle by extracting shared concepts into a third module neither depends on directly

## RFC Issue Template

```
## RFC: [Module Name] — Deepen into [Proposed Interface]

## Problem
[Why the current structure causes friction — coupling, shallow interface, test pain]

## Proposed Interface
[The chosen interface design — methods, types, entry points]

## What It Hides
[Complexity moved inside the module]

## Dependency Strategy
[How cross-boundary or infrastructure dependencies are handled]

## Test Impact
[Which existing tests this replaces, and what boundary tests replace them]

## Trade-offs
[Honest downsides of this approach]
```
