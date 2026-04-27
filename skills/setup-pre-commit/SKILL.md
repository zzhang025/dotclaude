---
name: setup-pre-commit
description: Set up Husky.Net pre-commit hooks with CSharpier formatting, build checking, and tests in a .NET or Blazor repo. Use when user wants to add pre-commit hooks, set up Husky.Net, configure CSharpier, or add commit-time formatting/build-checking/testing to a .NET project.
---

# Setup Pre-Commit Hooks (.NET / Blazor)

## What This Sets Up

- **Husky.Net** pre-commit hook
- **CSharpier** formatting on staged `.cs` and `.razor` files
- **dotnet build** compile/type checking in the pre-commit hook
- **dotnet test** in the pre-commit hook

## Steps

### 1. Detect project type

Look for a `.sln` file or `*.csproj`. If neither exists, stop and tell the user this skill requires a .NET project.

### 2. Initialize tool manifest

If `.config/dotnet-tools.json` doesn't exist:

```bash
dotnet new tool-manifest
```

### 3. Install tools

```bash
dotnet tool install husky
dotnet tool install csharpier
```

### 4. Initialize Husky.Net

```bash
dotnet husky install
```

This creates the `.husky/` directory and registers the hook runner.

### 5. Create `.husky/pre-commit`

```bash
dotnet husky run
```

Make the file executable (`chmod +x .husky/pre-commit` on Unix; on Windows Git Bash this is handled automatically).

### 6. Create `task-runner.json`

Place at repo root:

```json
{
  "tasks": [
    {
      "name": "csharpier",
      "command": "dotnet",
      "args": ["csharpier", "--check", "."],
      "include": ["**/*.cs", "**/*.razor"]
    },
    {
      "name": "build",
      "command": "dotnet",
      "args": ["build", "--no-restore"]
    },
    {
      "name": "test",
      "command": "dotnet",
      "args": ["test", "--no-build"]
    }
  ]
}
```

**Adapt**: If no test project exists in the solution, omit the `test` task and tell the user.

### 7. Create `.csharpierrc.json` (if missing)

Only create if no CSharpier config exists. Use these defaults:

```json
{
  "printWidth": 100
}
```

### 8. Verify

- [ ] `.husky/pre-commit` exists and contains `dotnet husky run`
- [ ] `task-runner.json` exists at repo root
- [ ] `.config/dotnet-tools.json` lists both `husky` and `csharpier`
- [ ] CSharpier config exists
- [ ] Run `dotnet tool restore` to confirm tools install cleanly

### 9. Commit

Stage all changed/created files and commit with message: `Add pre-commit hooks (husky.net + csharpier)`

This will run through the new pre-commit hooks — a good smoke test that everything works.

## Notes

- `dotnet tool restore` re-installs all tools from the manifest — tell contributors to run this after cloning
- CSharpier handles both `.cs` (C#) and `.razor` (Blazor components) natively
- `dotnet build --no-restore` is fast — it skips package restore but still type-checks the whole solution
- `dotnet test --no-build` skips rebuilding, relying on the build step above
