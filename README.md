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

> **Windows:** Enable Developer Mode (Settings → System → For developers) to allow unprivileged symlinks, or run Git Bash as Administrator.

**1. Clone the repo**
```bash
git clone git@github.com:<you>/dotclaude.git ~/.claude-config
```

**2. Run the installer**
```bash
cd ~/.claude-config
chmod +x install.sh
./install.sh
```

This creates symlinks from the repo into the right locations:

| Repo file | Linked to |
|---|---|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `settings.json` | `~/.claude/settings.json` |
| `skills/` | `~/.claude/skills` |
| `ccstatusline/settings.json` | `~/.config/ccstatusline/settings.json` |

Any existing files at those paths are backed up with a `.bak` suffix automatically.

**3. Authenticate Claude Code**
```bash
claude   # → follow login prompt
```

## Sync (Existing Machine)

```bash
cd ~/.claude-config && git pull
# Symlinks are live — no reinstall needed
```

## Machine-Specific Overrides

Use `~/.claude/settings.local.json` (gitignored) for machine-specific settings like local tool paths.
