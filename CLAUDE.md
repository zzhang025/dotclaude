# Personal Claude Code Instructions

Personal instructions injected into every Claude Code session. Add your coding preferences, stack context, and workflow rules here.

For project-specific instructions, use `.claude/CLAUDE.md` inside each project repo.

---

## Coding Preferences

- Primary language: C#
- Frontend: Blazor (Server and/or WASM)
- Framework: .NET (ASP.NET Core)
- Testing: xUnit, NSubstitute
- Formatting: CSharpier
- Pre-commit hooks: Husky.Net

## Stack Context

- All projects are C# / .NET unless stated otherwise
- UI is Blazor — prefer Razor components; use JS interop sparingly
- Dependency injection is standard; prefer constructor injection
- Async/await throughout; use `Task`/`ValueTask` appropriately
- Follow .NET naming conventions (PascalCase for public members, camelCase for locals)

## Workflow Rules

<!-- How you like Claude to behave: commit style, testing approach, communication style -->

### Git Safety

**Always ask before running any of these commands — no exceptions:**

| Command | Risk |
|---------|------|
| `git push --force` / `-f` | Overwrites remote history |
| `git push --force-with-lease` | Still rewrites shared history |
| `git reset --hard` | Discards uncommitted changes permanently |
| `git checkout -- .` / `git restore .` | Discards uncommitted changes permanently |
| `git clean -f` / `-fd` / `-fdx` | Deletes untracked files permanently |
| `git branch -D` | Force-deletes branch; may lose unmerged commits |
| `git stash drop` / `git stash clear` | Permanently removes stashed changes |
| `git commit --amend` | Rewrites history; dangerous if already pushed |
| `git rebase` (any form) | Rewrites history |
| `git tag -d` / `git push --delete` | Removes tags or remote refs |

User approval once does NOT mean approval in all future contexts. Ask each time.

### Safe Commands (No Confirmation Needed)

Run these freely without asking:

**Git — read-only:** `git status`, `git log`, `git diff`, `git show`, `git branch` (listing), `git fetch`, `git stash list`, `git remote -v`

**Shell — read-only:** `ls`, `find`, `cat`, `head`, `tail`, `grep`, `rg`, `echo`, `pwd`, `which`, `env`

**Build / test:** dependency installs (`npm install`, `dotnet restore`, `pip install`), test runners, linters, build commands

Anything not clearly on this list — ask first.
