# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

Personal Claude Code global configuration ("dotfiles for Claude Code") — versioned in git, deployed via symlinks. It contains global session instructions, plugin settings, custom skills (slash commands), and terminal status line config.

## Deployment

```bash
chmod +x install.sh && ./install.sh
```

Creates symlinks:
- `CLAUDE.md` → `~/.claude/CLAUDE.md`
- `settings.json` → `~/.claude/settings.json`
- `skills/` → `~/.claude/skills`
- `ccstatusline/settings.json` → `~/.config/ccstatusline/settings.json`

Changes take effect immediately via symlinks — no reinstall needed after `git pull`.

**Windows:** Enable Developer Mode or run Git Bash as Administrator to allow unprivileged symlinks.

Machine-specific overrides go in `~/.claude/settings.local.json` (gitignored, not in this repo).

## Architecture

### Root Config
- `CLAUDE.md` — global session instructions injected into every Claude Code session; intentionally left as a template for the user to fill in
- `settings.json` — enables plugins and configures the `ccstatusline` statusLine hook

### Skills (`skills/<name>/SKILL.md`)
Each skill is a slash command invoked via `/skill-name`. Current skills:
- `tdd` — test-driven development workflow with supporting reference docs (`tests.md`, `mocking.md`, `refactoring.md`, `interface-design.md`, `deep-modules.md`)
- `qa` — conversational QA session + GitHub issue filing with blocking relationships
- `design-an-interface` — "Design It Twice" interface exploration methodology
- `setup-pre-commit` — Husky.Net + CSharpier for .NET/Blazor projects
- `grill-me` — intensive interview to stress-test plans before implementation
- `write-a-skill` — meta-skill for creating new skills in this repo
- `frontend-skill` — production-grade frontend design principles

### ccstatusline
Terminal status line widget config. Displays model, context %, git branch, git changes, and session usage.

## Adding a New Skill

Use the `write-a-skill` skill (`/write-a-skill`) — it guides the full creation process. Each skill lives in its own directory under `skills/` with a `SKILL.md` file. Supporting reference documents can sit alongside it.

## Key Files to Know

- `settings.json` — add/remove plugins here; see the `plugins` array
- `skills/tdd/` — most complex skill, has 5 supporting reference docs
- `install.sh` — idempotent; safe to re-run; backs up existing files with `.bak`
