# Specmark — Specification-Driven Change Workflow Skill

[![GitHub Release](https://img.shields.io/github/v/release/Kirky-X/specmark?style=flat-square)](https://github.com/Kirky-X/specmark/releases)
[![GitHub License](https://img.shields.io/github/license/Kirky-X/specmark?style=flat-square)](LICENSE)

Specmark is an AI-agent-oriented specification-driven change management skill. It is the successor to four separate `specmark-*` top-level skills, now flattened and merged into a single skill. It provides a complete workflow through four subcommands: `explore` (read-only exploration/clarification) → `propose` (one-shot generation of proposal + design + tasks) → `apply` (execute tasks.md item by item) → `archive` (archive completed changes and evaluate delta spec synchronization).

Specmark is a **pure documentation skill** with no external CLI dependency: all change-management operations are performed by the AI agent's file-system tools directly against the `specmark/` working directory. The complete flow, steps, and guardrails for each subcommand are documented in [SKILL.md](SKILL.md) and `references/<subcommand>.md`.

## Features

- **Four-stage spec-driven workflow**: explore → propose → apply → archive. Non-strictly linear; stages can be skipped as needed.
- **One-shot artifact generation**: `propose` produces `proposal.md` + `design.md` + `tasks.md` in a single run.
- **Read-only thinking mode**: `explore` writes no application code — used to clarify ideas, compare options, refine requirements.
- **Per-task tracking**: `apply` checks off progress against `tasks.md` and supports resuming an interrupted change.
- **Delta spec evaluation on archive**: `archive` automatically evaluates whether to sync delta specs into `specmark/specs/`.
- **Single entry point**: one skill, with subcommand routing via `$ARGUMENTS[0]`.

## Installation

### Option 1: Install via the `skills` package (recommended)

Requires [Node.js](https://nodejs.org/) 18+ and the `skills` npm package (v1.5.12+). `skills` is the CLI of the open agent skills ecosystem and supports 68+ agents (Claude Code / Trae / Cursor / Codex / OpenCode, etc.).

```bash
# Install to Claude Code
npx skills add https://github.com/Kirky-X/specmark.git --agent claude-code -y

# Equivalent shorthand (owner/repo)
npx skills add Kirky-X/specmark --agent claude-code -y

# Install to Trae
npx skills add Kirky-X/specmark --agent trae -y

# List all discoverable skills in the repo (without installing)
npx skills add https://github.com/Kirky-X/specmark.git --list
```

After installation, skill files are placed in the agent's skills directory (e.g. `.claude/skills/specmark/`).

### Option 2: Traditional git clone

```bash
git clone https://github.com/Kirky-X/specmark.git
# Link or copy SKILL.md + references/ into the agent skills directory
# Example runtime skill paths (pick one):
#   Claude Code:  ~/.claude/skills/specmark/
#   Trae:         ~/.trae-cn/skills/specmark/
#   Cursor:       ~/.cursor/skills/specmark/
#   Codex:        ~/.codex/skills/specmark/
```

### No External Dependencies

Specmark is a pure documentation skill — no external CLI installation required. All change-management operations are performed by the AI agent's file-system tools directly.

## Usage Examples

Once Specmark is loaded as a skill, subcommands are selected via `$ARGUMENTS[0]`, and natural-language intent is also supported. See the [SKILL.md routing table](./SKILL.md) for detailed subcommand descriptions and intent routing.

| Subcommand | One-line function                                                    |
| ---------- | -------------------------------------------------------------------- |
| `explore`  | Read-only exploration/thinking mode; clarify ideas, compare options  |
| `propose`  | One-shot generation of proposal + design + tasks artifacts           |
| `apply`    | Execute tasks defined in tasks.md, checking off each item            |
| `archive`  | Archive a completed change, including delta spec sync evaluation     |

### Invocation examples

```text
/specmark propose add-user-auth      # Explicit subcommand + change name, full artifacts
/specmark apply                      # Execute / continue the current change
/specmark archive                    # Archive a completed change
/specmark explore                    # Enter read-only exploration mode
/specmark                            # No argument → print subcommand routing table
```

### Natural-language intent triggers

```text
"I want to do X / add a feature"        → propose (generate full proposal)
"Help me think this through / compare options" → explore
"Start implementing / do the next task" → apply
"This change is done / archive it"      → archive
"I'm not sure yet / let's talk first"   → explore (confirmed via AskUserQuestion)
```

## Capability Overview

### `references/` — Subcommand flow documents

Complete Steps + Guardrails reference for each subcommand:

| File                       | Subcommand flow                                            |
| -------------------------- | ---------------------------------------------------------- |
| [`explore.md`](references/explore.md)   | explore flow (read-only exploration/clarification)         |
| [`propose.md`](references/propose.md)   | propose flow (generate full proposal artifacts)            |
| [`apply.md`](references/apply.md)       | apply flow (execute against tasks.md)                     |
| [`archive.md`](references/archive.md)   | archive flow (archive + delta spec evaluation)             |

### `specmark/` — Change and spec storage

```
specmark/
├── changes/    # In-progress changes (proposal/design/tasks)
└── specs/      # Sync target for archived delta specs
```

### `test-prompts.json` — Subcommand trigger test cases

Contains trigger-phrase test cases for each subcommand, used to verify skill routing correctness.

## Complete Workflow Chain

```
explore (exploration/clarification) → propose (generate proposal) → apply (execute) → archive (archive)
(read-only thinking)                  (proposal/design/tasks)        (per-task checkoff) (delta spec sync)
```

1. `explore` is a read-only thinking mode, enterable at any time; once the idea is clear, use `propose` to land it as a change.
2. After `propose` produces the full artifact set, it prompts you to run `/specmark apply`.
3. When all `apply` tasks are complete, it prompts you to archive (`/specmark archive`).
4. `archive` evaluates whether the delta spec needs to be synced into `specmark/specs/`.
5. The four stages are not strictly linear — you may jump between them (see each reference's Fluid Workflow Integration).

## Maintenance Notes

This skill was originally four separate top-level skills (`specmark-propose` / `specmark-explore` / `specmark-apply-change` / `specmark-archive-change`), now flattened and merged: each original `SKILL.md` had its frontmatter stripped and became `references/{propose,explore,apply,archive}.md`; cross-skill references (e.g. `/opsx:apply`, `specmark-continue-change`) have been rewritten as subcommands of this skill (`/specmark apply`, `/specmark propose`). The skill discovery mechanism only recognizes `specmark/SKILL.md` and does not independently pick up the flow documents inside `references/`.

## FAQ

### Required `skills` package version?

Requires `skills` npm package **v1.5.12+**. `skills` is the CLI of the [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) ecosystem and supports 68+ agents. Use `npx skills@latest` to automatically fetch the latest version.

### Remote install reports "No skills found"?

Confirm that the GitHub repo `Kirky-X/specmark` has been pushed with the latest code containing `SKILL.md` (at the repo root, with YAML frontmatter including `name` + `description`). The `skills` package clones the repo and scans for `SKILL.md`; an empty repo or missing `SKILL.md` triggers this error.

### `skills add` reports "Installation complete" but `.claude/skills/specmark/` does not exist?

This is a known issue with the `skills` package: the command reports success but does not actually copy files. **Workaround**: manually copy skill files into the agent skills directory (example paths for each runtime below — pick Claude Code / Trae / Cursor / Codex as needed):

```bash
# Claude Code
mkdir -p ~/.claude/skills/specmark
cp -r SKILL.md skill.json references ~/.claude/skills/specmark/

# Trae
mkdir -p ~/.trae-cn/skills/specmark
cp -r SKILL.md skill.json references ~/.trae-cn/skills/specmark/

# Cursor
mkdir -p ~/.cursor/skills/specmark
cp -r SKILL.md skill.json references ~/.cursor/skills/specmark/

# Codex
mkdir -p ~/.codex/skills/specmark
cp -r SKILL.md skill.json references ~/.codex/skills/specmark/
```

## License

MIT
