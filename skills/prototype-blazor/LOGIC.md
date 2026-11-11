# Logic Prototype

A tiny interactive console app that lets the user drive a state model by hand. Use this when the question is about **business logic, state transitions, or data shape** — the kind of thing that looks reasonable on paper but only feels wrong once you push it through real cases.

## When this is the right shape

- "I'm not sure if this state machine handles the edge case where X then Y."
- "Does this data model actually let me represent the case where..."
- "I want to feel out what the API should look like before writing it."
- Anything where the user wants to **press buttons and watch state change**.

If the question is "what should this look like" — wrong branch. Use [UI.md](UI.md).

## Process

### 1. State the question

Before writing code, write down what state model and what question you're prototyping. One paragraph, in the prototype's README or a comment at the top of the file. A logic prototype that answers the wrong question is pure waste — make the question explicit so it can be checked later, whether the user is watching now or returning to it AFK.

### 2. Pick the shape

Use C#. Match the project's existing conventions — don't introduce a new framework just for the prototype.

### 3. Isolate the logic in a portable module

Put the actual logic — the bit that's answering the question — behind a small, pure interface that could be lifted out and dropped into the real codebase later. The console shell around it is throwaway; the logic module shouldn't be.

The right shape depends on the question:

- **A pure reducer** — `(TState state, TAction action) => TState`. Good when actions are discrete events and state is a single value. Implement as a static method or record.
- **A state machine** — explicit states and transitions. Good when "which actions are even legal right now" is part of the question. Use a `switch` on a discriminated union (record hierarchy) or an enum state field.
- **A small set of pure static methods** over a plain data type. Good when there's no implicit current state — just transformations.
- **A class with a clear method surface** when the logic genuinely owns ongoing internal state.

Keep it pure: no Console I/O, no side effects inside the logic module. The console shell imports it and calls into it; nothing flows the other direction.

This is what makes the prototype useful past its own lifetime. When the question's been answered, the validated reducer / machine / function set can be lifted into the real module — the console shell gets deleted.

### 4. Build the smallest console app that exposes the state

Build as a **lightweight console app** — on every tick, clear the screen (`Console.Clear()`) and re-render the whole frame. The user should always see one stable view, not an ever-growing scrollback.

Each frame has two parts, in this order:

1. **Current state**, pretty-printed (one field per line or formatted JSON via `System.Text.Json`). Use `Console.ForegroundColor` for emphasis — bold/highlight field names or important values, dim less important context. Reset with `Console.ResetColor()`.
2. **Keyboard shortcuts**, listed at the bottom: `[a] add item  [d] delete  [t] tick  [q] quit`.

Behaviour:

1. **Initialise state** — a single in-memory object. Render the first frame on start.
2. **Read one keystroke** at a time via `Console.ReadKey(intercept: true)`, dispatch to a handler.
3. **Re-render** the full frame after every action — don't append, replace (`Console.Clear()`).
4. **Loop until quit** (`q` key or `Escape`).

The whole frame should fit on one screen.

### 5. Make it runnable in one command

Structure the prototype as a minimal console app project (`.csproj` targeting `net9.0` or the project's current TFM). The user runs:

```
dotnet run --project path/to/Prototype.csproj
```

If the host project has a `Makefile` or `justfile`, add a target there. Otherwise, put the command in a comment at the top of `Program.cs`.

### 6. Hand it over

Give the user the run command. They'll drive it themselves; the interesting moments are when they say "wait, that shouldn't be possible" or "huh, I assumed X would be different" — those are the bugs in the _idea_, which is the whole point. If they want new actions added, add them. Prototypes evolve.

### 7. Capture the answer

When the prototype has done its job, the answer to the question is the only thing worth keeping. If the user is around, ask what it taught them. If not, leave a `NOTES.md` next to the prototype so the answer can be filled in (or filled in by you, if you've watched the session) before the prototype gets deleted.

## Anti-patterns

- **Don't add tests.** A prototype that needs tests is no longer a prototype.
- **Don't wire it to the real database.** Use in-memory collections unless the question is specifically about persistence.
- **Don't generalise.** No "what if we wanted to support X later." The prototype answers one question.
- **Don't blur the logic and the console shell together.** If the reducer / state machine references `Console.WriteLine` or `Console.ReadKey`, it's no longer portable. Keep the console shell as a thin wrapper over a pure class/module.
- **Don't ship the console shell into production.** The shell is optimised for being driven by hand from a terminal. The logic module behind it is the bit worth keeping.
