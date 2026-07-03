# Specmark — Specification-Driven Change Workflow Skill

[![GitHub Release](https://img.shields.io/github/v/release/Kirky-X/specmark?style=flat-square)](https://github.com/Kirky-X/specmark/releases)
[![GitHub License](https://img.shields.io/github/license/Kirky-X/specmark?style=flat-square)](LICENSE)

Specmark is an AI-agent-oriented specification-driven change management skill. It is the successor to four separate `specmark-*` top-level skills, now flattened and merged into a single skill. It provides a complete workflow through seven subcommands: `explore` (read-only exploration/thinking) → `clarify` (structured clarification) → `propose` (one-shot generation of proposal + design + tasks) → `analyze` (cross-artifact consistency check) → `apply` (execute tasks.md item by item) → `converge` (reconcile code against spec) → `archive` (archive completed changes and evaluate delta spec synchronization).

Specmark is a **pure documentation skill** with no external CLI dependency: all change-management operations are performed by the AI agent's file-system tools directly against the `specmark/` working directory. The complete flow, steps, and guardrails for each subcommand are documented in [SKILL.md](SKILL.md) and `references/<subcommand>.md`.

## Features

- **Seven-stage spec-driven workflow**: explore → clarify → propose → analyze → apply → converge → archive. Non-strictly linear; stages can be skipped as needed.
- **Auto-execution chain**: Stages auto-link (explore→clarify→propose→analyze→apply→converge→ask next), no manual stepping required.
- **One-shot artifact generation**: `propose` produces `proposal.md` + `design.md` + `tasks.md` in a single run.
- **Long-running change auto-generates delta spec**: When tasks ≥ 5 or spanning ≥ 3 modules, automatically creates `specs/<capability>/spec.md` with verifiable requirements.
- **Read-only thinking mode**: `explore` writes no application code — used to clarify ideas, compare options, refine requirements.
- **Structured clarification**: `clarify` scans 8 categories, asks at most 5 high-impact questions.
- **Cross-artifact quality gate**: `analyze` read-only checks proposal/design/tasks/delta-spec consistency.
- **Per-task tracking**: `apply` checks off progress against `tasks.md` and supports resuming an interrupted change.
- **Convergence reconciliation**: `converge` compares code against spec (prioritizes delta spec acceptance criteria), append-only adds missing tasks.
- **Delta spec evaluation on archive**: `archive`'s `--sync` flag syncs delta specs into `specmark/specs/` main specs.
- **Mermaid flow diagrams**: Stage collaboration chain, auto-execution chain, and usage examples visualized as Mermaid diagrams.
- **Auto-chain failure modes**: 7 failure conditions with predefined handling (analyze CRITICAL pauses chain, converge loop hard-capped at 3, etc.).
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

After installation, skill files are placed in the agent's skills directory (the exact path is determined by the chosen `--agent`; refer to each runtime's documentation).

### Option 2: Traditional git clone + install-skill.sh

The repo ships with `scripts/install-skill.sh`, which supports 9 agents (claude / cursor / windsurf / trae / gemini / copilot / opencode / roocode / qoder) for one-shot installation:

```bash
git clone https://github.com/Kirky-X/specmark.git
cd specmark

# Install to the claude agent directory of the current project
./scripts/install-skill.sh install specmark --agent claude

# Install to all supported agents
./scripts/install-skill.sh install specmark --all-agents

# List supported agents and their paths
./scripts/install-skill.sh list-agents
```

The script automatically copies `SKILL.md` + `skill.json` + `references/` into the target runtime's skills directory. For manual installation, use the `list-agents` subcommand to look up each runtime's path and copy files yourself.

### Updating

Skills installed via `install-skill.sh` support one-command updates:

```bash
# Update a single skill (git pull + reinstall)
./scripts/install-skill.sh update specmark --agent claude

# Update all skills
./scripts/install-skill.sh update --agent claude

# Update to all agents
./scripts/install-skill.sh update specmark --all-agents
```

Skills installed via `npx skills add` require re-running `npx skills add` to pull the latest version.

## Usage Examples

Once Specmark is loaded as a skill, subcommands are selected via `$ARGUMENTS[0]`, and natural-language intent is also supported. See the [SKILL.md routing table](./SKILL.md) for detailed subcommand descriptions and intent routing.

| Subcommand | One-line function                                                    |
| ---------- | -------------------------------------------------------------------- |
| `explore`  | Read-only exploration/thinking mode; clarify ideas, compare options  |
| `clarify`  | Structured clarification, optional before propose (≤5 high-impact questions, 8-category scan) |
| `propose`  | One-shot generation of proposal + design + tasks artifacts           |
| `analyze`  | Cross-artifact consistency analysis (read-only quality gate, after propose before apply) |
| `apply`    | Execute tasks defined in tasks.md, checking off each item            |
| `converge` | Reconcile: compare code against spec after apply, append missing tasks |
| `archive`  | Archive a completed change, including delta spec sync evaluation     |

### Invocation examples

```text
/specmark propose add-user-auth      # Explicit subcommand + change name, full artifacts
/specmark clarify add-user-auth      # Clarify ambiguities before propose (≤5 questions, 8-category scan)
/specmark analyze add-user-auth      # Check proposal/design/tasks consistency (read-only gate)
/specmark apply                      # Execute / continue the current change
/specmark converge                   # Compare code against spec, append missing tasks
/specmark explore                    # Enter read-only exploration mode
/specmark                            # No argument → print subcommand routing table
```

### Natural-language intent triggers

```text
"I want to do X / add a feature"        → propose (generate full proposal)
"Requirements have ambiguities / ask first" → clarify (structured clarification)
"Help me think this through / compare options" → explore
"Proposal done / check artifact consistency" → analyze (read-only gate)
"Start implementing / do the next task" → apply
"Implementation done / compare code and spec" → converge
"This change is done / archive it"      → archive
"I'm not sure yet / let's talk first"   → explore (confirmed via AskUserQuestion)
```

## Capability Overview

### `references/` — Subcommand flow documents

Complete Steps + Guardrails reference for each subcommand:

| File                       | Subcommand flow                                            |
| -------------------------- | ---------------------------------------------------------- |
| [`explore.md`](references/explore.md)     | explore flow (read-only exploration/thinking, incl. deep research mode) |
| [`clarify.md`](references/clarify.md)     | clarify flow (structured clarification, 8-category scan)   |
| [`propose.md`](references/propose.md)     | propose flow (generate full proposal artifacts + templates)|
| [`analyze.md`](references/analyze.md)     | analyze flow (read-only cross-artifact consistency check)  |
| [`apply.md`](references/apply.md)         | apply flow (execute against tasks.md)                      |
| [`converge.md`](references/converge.md)   | converge flow (reconcile code vs spec gaps)                |
| [`archive.md`](references/archive.md)     | archive flow (archive + delta spec evaluation)             |

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
explore (exploration) → clarify (clarification) → propose (generate proposal) → analyze (consistency analysis) → apply (execute) → converge (reconcile) → archive (archive)
(read-only thinking)     (8-category Q&A)          (proposal/design/tasks)        (read-only gate)              (per-task checkoff) (append gaps)        (delta spec sync)
```

1. `explore` is a read-only thinking mode, enterable at any time; once the idea is clear, use `clarify` (optional) or `propose` to land it as a change.
2. `clarify` is an optional clarification step before `propose`; skip if the request is already concrete.
3. After `propose` produces the full artifact set, it prompts you to run `/specmark analyze` (optional gate) or `/specmark apply`.
4. `analyze` is an optional read-only quality gate after propose and before apply; it does not block apply.
5. When all `apply` tasks are complete, it prompts you to run `/specmark converge` before `/specmark archive`.
6. `converge` is an optional reconciliation step between apply and archive; append-only adds missing tasks, then returns to `apply` to close them.
7. The seven stages are not strictly linear — clarify/analyze/converge can all be skipped as needed (see each reference's Fluid Workflow Integration).

## Maintenance Notes

This skill was originally four separate top-level skills (`specmark-propose` / `specmark-explore` / `specmark-apply-change` / `specmark-archive-change`), now flattened and merged: each original `SKILL.md` had its frontmatter removed and became `references/{propose,explore,apply,archive}.md`; cross-skill references were rewritten as subcommands of this skill (`/specmark apply`, `/specmark propose`). The skill discovery mechanism only recognizes `specmark/SKILL.md` and does not independently fetch flow documents inside `references/`.

## FAQ

### Required `skills` package version?

Requires `skills` npm package **v1.5.12+**. `skills` is the CLI of the [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) ecosystem and supports 68+ agents. Use `npx skills@latest` to automatically fetch the latest version.

### Remote install reports "No skills found"?

Confirm that the GitHub repo `Kirky-X/specmark` has been pushed with the latest code containing `SKILL.md` (at the repo root, with YAML frontmatter including `name` + `description`). The `skills` package clones the repo and scans for `SKILL.md`; an empty repo or missing `SKILL.md` triggers this error.

### `skills add` reports "Installation complete" but the skill directory does not exist?

This is a known issue with the `skills` package: the command reports success but does not actually copy files. **Workaround**: reinstall using the repo's bundled install script, which supports multiple runtimes:

```bash
# Reinstall to a specific agent using install-skill.sh
./scripts/install-skill.sh install specmark --agent claude

# Or list all supported agent paths and copy manually
./scripts/install-skill.sh list-agents
```

For manual copying, `list-agents` displays each runtime's `folder/subdir` path; pick one and copy `SKILL.md` + `skill.json` + `references/` there.

## License

MIT
