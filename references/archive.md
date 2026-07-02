# Archive — Archive a completed change

Archive a completed change in the specmark workflow.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **If no change name provided, prompt for selection**

   Use the **Glob tool** to list `specmark/changes/*/` directories. Use the **AskUserQuestion tool** to let the user select.

   Show only active changes (not already archived).
   Include the schema used for each change if available.

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Check artifact completion status**

   Read `specmark/changes/<name>/tasks.md` checkbox state (`- [ ]` incomplete / `- [x]` complete) to check artifact completion.

   This tells you:
   - `schemaName`: The workflow being used
   - `artifacts`: List of artifacts with their status (`done` or other)

   **If any artifacts are not `done`:**
   - Display warning listing incomplete artifacts
   - Use **AskUserQuestion tool** to confirm user wants to proceed
   - Proceed if user confirms

3. **Check task completion status**

   Read the tasks file (typically `tasks.md`) to check for incomplete tasks.

   Count tasks marked with `- [ ]` (incomplete) vs `- [x]` (complete).

   **If incomplete tasks found:**
   - Display warning showing count of incomplete tasks
   - Use **AskUserQuestion tool** to confirm user wants to proceed
   - Proceed if user confirms

   **If no tasks file exists:** Proceed without task-related warning.

4. **Assess delta spec sync state**

   Check for delta specs at `specmark/changes/<name>/specs/`. If none exist, proceed without sync prompt.

   **If delta specs exist:**
   - Compare each delta spec with its corresponding main spec at `specmark/specs/<capability>/spec.md`
   - Determine what changes would be applied (adds, modifications, removals, renames)
   - Show a combined summary before prompting

   **Prompt options:**
   - If changes needed: "Sync now (recommended)", "Archive without syncing"
   - If already synced: "Archive now", "Sync anyway", "Cancel"

   If user chooses sync, use the Task tool to spawn an agent (subagent_type: "general-purpose") that syncs the delta specs into the main specs at `specmark/specs/<capability>/spec.md` (agent-driven: apply the analyzed delta — adds, modifications, removals, renames — to the corresponding main spec files). Pass the analyzed delta spec summary in the prompt. Proceed to archive regardless of choice.

5. **Perform the archive**

   Create the archive directory if it doesn't exist:

   ```bash
   mkdir -p docs/changes/archive
   ```

   Generate target name using current date: `YYYY-MM-DD-<change-name>`

   **Check if target already exists:**
   - If yes: Fail with error, suggest renaming existing archive or using different date
   - If no: Move the change directory to archive

   ```bash
   mv specmark/changes/<name> docs/changes/archive/YYYY-MM-DD-<name>
   ```

6. **Display summary**

   Show archive completion summary including:
   - Change name
   - Schema that was used
   - Archive location
   - Whether specs were synced (if applicable)
   - Note about any warnings (incomplete artifacts/tasks)

**Output On Success**

```
## Archive Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Archived to:** docs/changes/archive/YYYY-MM-DD-<name>/
**Specs:** ✓ Synced to main specs (or "No delta specs" or "Sync skipped")

All artifacts complete. All tasks complete.
```

**Guardrails**

- Always prompt for change selection if not provided
- Read `specmark/changes/<name>/tasks.md` checkbox state for completion checking
- Don't block archive on warnings - just inform and confirm
- The change directory moves wholesale to archive; no separate config file is involved
- Show clear summary of what happened
- If sync is requested, drive it agent-side: apply the delta spec changes to the main specs
- If delta specs exist, always run the sync assessment and show the combined summary before prompting
