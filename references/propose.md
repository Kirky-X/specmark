# Propose — Create a change with all artifacts in one step

Propose a new change - create the change and generate all artifacts in one step.

I'll create a change with artifacts:

- proposal.md (what & why)
- design.md (how)
- tasks.md (implementation steps)

When ready to implement, run `/specmark apply`

---

**Input**: The user's request should include a change name (kebab-case) OR a description of what they want to build.

**Steps**

1. **If no clear input provided, ask what they want to build**

   Use the **AskUserQuestion tool** (open-ended, no preset options) to ask:

   > "What change do you want to work on? Describe what you want to build or fix."

   From their description, derive a kebab-case name (e.g., "add user authentication" → `add-user-auth`).

   **IMPORTANT**: Do NOT proceed without understanding what the user wants to build.

2. **Create the change directory**

   Use the **mkdir** operation to create `specmark/changes/<name>/`. The directory itself is the change record — no separate config file is used.

3. **Check existing progress**

   Read `specmark/changes/<name>/tasks.md` and inspect its checkbox state (`- [ ]` incomplete / `- [x]` complete) to understand what has already been done. If `tasks.md` does not exist, this is a freshly created change and nothing has been written yet.

4. **Create artifacts in sequence until apply-ready**

   Use the **TodoWrite tool** to track progress through the artifacts.

   specmark provides its own artifact templates — `proposal.md` / `design.md` / `tasks.md` — defined in the **Task Authoring Standards** section below and in this skill's `references/`. No external CLI is consulted for instructions.

   Loop through artifacts in dependency order (artifacts with no pending dependencies first):

   a. **For each artifact that is `ready` (dependencies satisfied)**:
   - Use the specmark artifact templates (structure defined below and in `references/`) as the structure for your output file
   - Read any completed dependency files for context (e.g., read `proposal.md` and `design.md` before writing `tasks.md`)
   - Write the artifact file at `specmark/changes/<name>/<artifact>.md`
   - Show brief progress: "Created <artifact-id>"

   b. **Continue until all required artifacts are complete**
   - After creating each artifact, re-read `specmark/changes/<name>/tasks.md` checkbox state to confirm progress
   - Stop when `proposal.md`, `design.md`, and `tasks.md` all exist and `tasks.md` lists every committed task

   c. **If an artifact requires user input** (unclear context):
   - Use **AskUserQuestion tool** to clarify
   - Then continue with creation

5. **Show final status**
   Read `specmark/changes/<name>/tasks.md` and report the checkbox progress.

**Output**

After completing all artifacts, summarize:

- Change name and location
- List of artifacts created with brief descriptions
- What's ready: "All artifacts created! Ready for implementation."
- Prompt: "Run `/specmark apply` or ask me to implement to start working on the tasks."

**Artifact Creation Guidelines**

- Follow the specmark artifact templates (proposal.md / design.md / tasks.md) defined in **Task Authoring Standards** below and this skill's `references/`
- Read dependency artifacts for context before creating new ones (e.g., read `proposal.md` and `design.md` before writing `tasks.md`)
- Use the template structure as the skeleton for your output file - fill in its sections
- **IMPORTANT**: Template instructions and guidance are constraints for YOU, not content for the file
  - Do NOT copy template commentary, examples, or placeholder markers into the artifact
  - These guide what you write, but should never appear in the output

**Guardrails**

- Create ALL artifacts needed for implementation (proposal.md, design.md, and tasks.md)
- Always read dependency artifacts before creating a new one
- If context is critically unclear, ask the user - but prefer making reasonable decisions to keep momentum
- If a change with that name already exists, ask if user wants to continue it or create a new one
- Verify each artifact file exists after writing before proceeding to next
- **Order tasks sequentially** — in `tasks.md`, list tasks in execution/dependency order. Downstream `/specmark apply` enforces strict sequential execution (no skipping), so sequence them so each task can complete before the next begins

---

## Task Authoring Standards

The following standards apply when authoring `tasks.md`. They are mandatory; `apply` and `converge` both assume tasks conform to them.

### 1. Task format — 5 elements

Every task line uses this exact shape:

```
- [ ] [T###] [P?] [Story?] Description with file path
```

| Element       | Required | Meaning                                                            |
| ------------- | -------- | ----------------------------------------------------------------- |
| `- [ ]`       | yes      | Checkbox; flipped to `- [x]` by `apply` on completion            |
| `[T###]`      | yes      | Zero-padded stable ID (T001, T002...). Never renumber existing IDs |
| `[P?]`        | yes      | Priority: P0 (blocker) / P1 (must) / P2 (nice). Used by converge  |
| `[Story?]`    | optional | Story ID if the change is tracked against a backlog story        |
| Description   | yes      | Imperative, concrete, **must include the file path** being changed |

Example:

```
- [ ] [T003] [P1] [AUTH-12] Add rate-limit middleware to src/auth/login.ts (10 req/min/IP)
```

A task without a file path is almost always under-specified — fix the description, don't waive the rule.

### 2. No Placeholders — hard rule

Tasks must be implementable as written, with no decisions deferred. The following phrasings are **forbidden** in task descriptions:

- `TBD`, `TODO`, `FIXME`, `???`, `<...>`
- "add appropriate error handling" (what counts as appropriate?)
- "handle edge cases" (which cases?)
- "similar to Task N" (write the actual steps; references drift)
- "write tests for the above" (state what behavior the test asserts)
- "as needed" / "if relevant" / "where appropriate"

If you cannot write the concrete behavior, the task is under-specified — either split it into concrete sub-tasks or route the open question to `## NEEDS CLARIFICATION` (below).

### 3. Bite-sized TDD granularity

Each task should represent **2-5 minutes of focused work**, not a multi-hour epic. If a task would take longer, split it. The preferred shape for any code-producing task is the **TDD five-step cycle**, encoded as either one task with five sub-bullets or five consecutive tasks:

1. **Red** — write a failing test that pins the desired behavior
2. **Green** — write the minimum code to make the test pass
3. **Refactor** — improve structure without changing behavior
4. **Commit** — `git commit -m "feat(<area>): <description>"`
5. **Verify** — run the affected test suite; confirm green

Granularity test: if you cannot name the single file and single behavior change in one sentence, the task is too big.

### 4. Self-Review — three checks before finishing

After drafting all tasks, run these three checks before declaring the change apply-ready. Failures must be fixed before hand-off to `apply`.

| Check              | What it verifies                                                          |
| ------------------ | ------------------------------------------------------------------------- |
| **Spec coverage**  | Every requirement in `proposal.md` and every decision in `design.md` maps to ≥1 task. Unmapped requirements go to NEEDS CLARIFICATION or get a task. |
| **Placeholder scan** | Grep tasks.md for the forbidden phrases in §2. Zero matches required.   |
| **Type consistency** | Task IDs are zero-padded and unique; priorities are from {P0,P1,P2}; file paths in descriptions point at files that exist or will be created by an earlier task. |

### 5. NEEDS CLARIFICATION — bounded bail-out

If, after self-review, a requirement still cannot be turned into a concrete task, record it under a `## NEEDS CLARIFICATION` section at the bottom of `proposal.md` (not `tasks.md` — tasks are commitments, clarifications are questions).

- **Hard cap: 3 items.** If you have 4+, run `/specmark clarify` first and come back.
- **Sort by impact**, highest first: `scope` > `security/privacy` > `UX` > `technical`. A scope ambiguity blocks more downstream work than a technical one.
- **Format each item** as:
  ```
  - **[<category>]** <what's unclear> — <why it blocks a task> — <default if user doesn't answer>
  ```
- `apply` will pause and prompt the user when it encounters a NEEDS CLARIFICATION item relevant to the current task; it does not silently pick the default.

**Hand-off note**: when propose finishes, the prompt to the user becomes: "All artifacts created. Run `/specmark apply` to implement. Optional: `/specmark analyze` for a consistency check first."
