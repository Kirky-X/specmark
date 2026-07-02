# Apply — Implement tasks from a specmark change

Implement tasks from a specmark change.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, use the **Glob tool** to list `specmark/changes/*/` directories and use the **AskUserQuestion tool** to let the user select

   Always announce: "Using change: <name>" and how to override (e.g., `/specmark apply <other>`).

2. **Check status to understand the schema**

   Read `specmark/changes/<name>/tasks.md` and inspect its checkbox state (`- [ ]` incomplete / `- [x]` complete) to understand progress.

   This tells you:
   - `schemaName`: The workflow being used (typically "spec-driven")
   - Which artifact contains the tasks (typically `tasks.md` for spec-driven)

3. **Read apply context**

   Read the artifacts under `specmark/changes/<name>/` — `proposal.md`, `design.md`, and `tasks.md` — as context for implementation.

   This gives you:
   - `contextFiles`: the artifact files in the change directory (proposal/design/tasks, plus any `specs/` deltas)
   - Progress (count `- [ ]` vs `- [x]` in `tasks.md` for total/complete/remaining)
   - Task list with status
   - Guidance for the current state

   **Handle states:**
   - If artifacts are missing (e.g., no `tasks.md`): show message, suggest using `/specmark propose` to create the missing artifacts first
   - If all tasks already `- [x]`: congratulate, suggest archive
   - Otherwise: proceed to implementation

4. **Read context files**

   Read every artifact file in the specmark change directory (`specmark/changes/<name>/`).
   The files depend on the schema being used:
   - **spec-driven**: proposal, specs, design, tasks
   - Other schemas: follow the contextFiles from the specmark change directory

5. **Show current progress**

   Display:
   - Schema being used
   - Progress: "N/M tasks complete"
   - Remaining tasks overview
   - Guidance for the current state

6. **Implement tasks (loop until done or blocked)**

   **Strict order — no skipping.** Work through tasks in the exact order they appear in `tasks.md`. Task N+1 may begin ONLY after task N is marked `- [x]`. Never jump ahead to a later task while an earlier one is still `- [ ]` — even if a later task looks easier, unblocks others, or seems more interesting. The sole permitted reason to leave a task `- [ ]` is a genuine blocker, and then you PAUSE (see below) — you do not skip to the next.

   For each task in order:
   - Show which task being worked on (e.g., "task 3/7: <description>")
   - Make the code changes required
   - Keep changes minimal and focused on that one task
   - Mark task complete in the tasks file IMMEDIATELY: `- [ ]` → `- [x]`
   - Only then advance to the next task in sequence

   **Pause if:**
   - Task is unclear → ask for clarification
   - Implementation reveals a design issue → suggest updating artifacts
   - Error or blocker encountered → report and wait for guidance
   - User interrupts

7. **On completion or pause, show status**

   Display:
   - Tasks completed this session
   - Overall progress: "N/M tasks complete"
   - If all done: suggest archive
   - If paused: explain why and wait for guidance

**Output During Implementation**

```
## Implementing: <change-name> (schema: <schema-name>)

Working on task 3/7: <task description>
[...implementation happening...]
✓ Task complete

Working on task 4/7: <task description>
[...implementation happening...]
✓ Task complete
```

**Output On Completion**

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1
- [x] Task 2
...

All tasks complete! Ready to archive this change.
```

**Output On Pause (Issue Encountered)**

```
## Implementation Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 4/7 tasks complete

### Issue Encountered
<description of the issue>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

**Guardrails**

- **No skipping tasks** — execute in `tasks.md` order; a task may start only after the previous one is `- [x]`. If a later task looks tempting or seems to unblock others, finish the current one first. Leaving a task incomplete to move on is never allowed — only a genuine blocker pauses you (per below)
- Keep going through tasks until done or blocked
- Always read context files before starting (from the apply instructions output)
- If task is ambiguous, pause and ask before implementing
- If implementation reveals issues, pause and suggest artifact updates
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
- Pause on errors, blockers, or unclear requirements - don't guess
- Use contextFiles from the specmark change directory, don't assume specific file names

---

## Pre-Implementation Critical Review

After step 5 (show current progress) and **before** step 6 (the implement-tasks loop), perform a critical review of `tasks.md`. This is a 30-second sanity check that catches problems cheaply, before any code is written.

**Checks (all must pass before entering the loop):**

1. **Placeholder scan** — grep `tasks.md` for the forbidden phrases defined in `propose.md` §2 (TBD / TODO / FIXME / "add appropriate error handling" / "handle edge cases" / "similar to Task N" / "write tests for the above" / "as needed" / "if relevant" / "where appropriate"). Zero matches required.
2. **File path presence** — every task description includes at least one file path. Tasks without a path are under-specified and will cause mid-implementation stalls.
3. **Hidden dependency check** — for each task N, verify that whatever task N+1 needs is actually produced by task N (or earlier). Sequential execution means a missing dependency blocks the whole chain.
4. **NEEDS CLARIFICATION scan** — read `proposal.md` for a `## NEEDS CLARIFICATION` section. If any item affects an early task, surface it to the user **now**, before starting, rather than stalling mid-implementation.

**On failure:**

- If placeholders or missing paths are found → suggest running `/specmark propose` to fix `tasks.md` before apply proceeds. Do not silently fix tasks yourself; that's propose's responsibility.
- If a hidden dependency is found → suggest reordering or splitting tasks via `/specmark propose`.
- If a NEEDS CLARIFICATION item blocks → prompt the user to resolve it (or accept the recorded default) before entering the loop.

**On success:** announce "Critical review passed" and proceed to step 6.

## Git Worktree Isolation (recommended for non-trivial changes)

For changes touching more than ~3 files or spanning multiple sessions, consider isolating implementation in a git worktree before step 6:

```bash
git worktree add ../<change-name>-worktree
cd ../<change-name>-worktree
```

**Why:**
- Keeps the main working tree clean for parallel work on other changes
- Easy to discard the whole attempt if implementation goes wrong (`git worktree remove`)
- The `tasks.md` checkboxes and any in-progress commits stay isolated from other branches
- Pairs naturally with the TDD commit-per-task discipline from `propose.md` §3

**When to skip:** trivial single-file changes, or when the user is already on a dedicated branch. Don't force worktree creation if it adds friction without value. Suggest it; don't require it.

## Finishing: Converge Then Archive

When step 7 reports "all done" (every task marked `- [x]`), **do not** jump straight to archive. The completion prompt is enhanced to a two-step hand-off:

1. **First prompt:** "All tasks complete. Run `/specmark converge` to reconcile tasks against the implemented code before archiving."
2. **After converge** closes any appended convergence tasks (re-running apply to flip those to `- [x]`), **then** prompt: "Run `/specmark archive` to archive this change."

**Why converge before archive:** archive moves the change directory into `archive/` and is hard to undo cleanly. Converge catches the common failure mode where the implementation drifted from the spec (missing edge cases, partial coverage, silent contradictions) while the drift is still cheap to fix. Skipping converge means archiving a change whose code doesn't fully match its spec — which corrupts the spec as a source of truth for future changes.

**Updated completion output:**

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** N/N tasks complete ✓

All tasks complete. Next steps:
1. `/specmark converge` — reconcile tasks vs. code (recommended)
2. `/specmark archive` — archive this change (run after converge)
```

**Fluid Workflow Integration**

This subcommand supports the "actions on a change" model:

- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions
- **Allows artifact updates**: If implementation reveals design issues, suggest updating artifacts - not phase-locked, work fluidly
