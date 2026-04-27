# dotclaude

Personal Claude Code global configuration — skills, settings, and third-party tooling — versioned in git and symlinked into place.

## Structure

```
dotclaude/
├── install.sh                        # Bootstrap: creates all symlinks
├── .gitignore
├── README.md
│
├── CLAUDE.md                         # Global instructions, injected into every session
├── settings.json                     # Global Claude Code settings + statusLine hook
│
├── skills/                           # Global skills + slash commands
│   └── <skill-name>/
│       └── SKILL.md
│
└── ccstatusline/
    └── settings.json                 # ccstatusline widget layout + theme config
```

## Symlink Map

| Repo path | Target |
|---|---|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `settings.json` | `~/.claude/settings.json` |
| `skills/` | `~/.claude/skills` |
| `ccstatusline/settings.json` | `~/.config/ccstatusline/settings.json` |

## Bootstrap (New Machine)

```bash
git clone git@github.com:<you>/dotclaude.git ~/.claude-config
cd ~/.claude-config && chmod +x install.sh && ./install.sh

# Authenticate Claude Code
claude   # → follow login prompt
```

> **Windows:** Run Git Bash as Administrator, or enable Developer Mode (Settings → System → For developers) to allow unprivileged symlinks.

## Sync (Existing Machine)

```bash
cd ~/.claude-config && git pull
# Symlinks are live — no reinstall needed
```

## Machine-Specific Overrides

Use `~/.claude/settings.local.json` (gitignored) for machine-specific settings like local tool paths.
