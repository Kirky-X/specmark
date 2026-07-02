# Analyze — Cross-artifact consistency check (read-only quality gate)

An optional quality gate between `propose` and `apply`. Reads `proposal.md`, `design.md`, and `tasks.md` for a change, detects consistency problems across them, and emits a Markdown report. **Read-only**: analyze never modifies any artifact.

**Positioning**: Optional, after `propose` and before `apply`. Use when the change is non-trivial (e.g., touches >1 module, multi-step tasks, or external integration) and a second look is worth the cost. Skip for trivial changes.

**Input**: Optionally specify a change name. If omitted, infer from context or use the Glob tool to list `specmark/changes/*/` directories (subdirectory names are change names).

**Steps**

1. **Locate the change and its artifacts**

   Read `specmark/changes/<name>/tasks.md`'s checkbox state (`- [ ]` pending / `- [x]` done) to confirm `proposal.md`, `design.md`, `tasks.md` all exist. If any is missing, emit a CRITICAL finding (see detection #6) and continue with what exists.

2. **Read all three artifacts in full**

   Read `proposal.md`, `design.md`, `tasks.md` end-to-end. Do not skim — cross-artifact inconsistencies only surface when you hold all three in mind.

3. **Run the 6 detection passes**

   For each pass, scan all three artifacts and record findings. Each finding has: detection type, severity, location, description.

   | # | Detection        | What it catches                                                       |
   | - | ---------------- | --------------------------------------------------------------------- |
   | 1 | Duplication      | Same requirement/task stated in two places with drift between them    |
   | 2 | Ambiguity        | Term or behavior with multiple plausible interpretations             |
   | 3 | Underdetermined  | Task that cannot be implemented without further decisions            |
   | 4 | Coverage gap     | Requirement in proposal/design with no corresponding task             |
   | 5 | Inconsistency    | proposal vs design vs tasks contradict each other on a concrete point |
   | 6 | Missing artifact | Required artifact absent (e.g., no tasks.md, no design.md)            |

4. **Assign severity to each finding**

   | Severity  | Meaning                                                                   |
   | --------- | ------------------------------------------------------------------------- |
   | CRITICAL  | Blocks apply — contradiction or missing artifact                          |
   | HIGH      | Will cause rework during apply — coverage gap on a core requirement       |
   | MEDIUM    | Ambiguity or underdetermined task; resolvable during apply with a note    |
   | LOW       | Cosmetic drift, duplicate wording; fix is optional                        |

5. **Cap at 50 findings**

   If more than 50 findings, keep the 50 highest-severity (CRITICAL → LOW) and append a final row: `... N more findings suppressed (run analyze again after fixing CRITICAL/HIGH)`.

6. **Emit the report — read-only, no file writes**

   Print the report to the conversation. Do **not** write it to disk and do **not** edit any artifact. If the user wants fixes applied, they run `propose` (to regenerate) or `converge` (post-apply).

**Output**

```
## Analyze Report — <change-name>

**Artifacts read:** proposal.md, design.md, tasks.md
**Findings:** N (CRITICAL: a | HIGH: b | MEDIUM: c | LOW: d)

| # | Severity   | Detection        | Location              | Finding                                             |
| - | ---------- | ---------------- | --------------------- | --------------------------------------------------- |
| 1 | CRITICAL   | Missing artifact | —                     | tasks.md absent                                     |
| 2 | HIGH       | Coverage gap     | proposal §2 / tasks   | "rate limiting" in proposal, no task implements it  |
| 3 | MEDIUM     | Underdetermined  | tasks T03             | "choose a cache strategy" — no decision recorded    |
| 4 | LOW        | Duplication      | design §1 / tasks T01 | Retry policy stated twice with different backoffs   |

**Recommendation:** Fix CRITICAL and HIGH before `/specmark apply`. MEDIUM/LOW can be resolved inline during apply.
```

**Guardrails**

- **Read-only** — never write to, edit, or move any artifact. Analyze observes; it does not act.
- **Max 50 findings** — cap is hard. Over-cap → keep highest severity, suppress the rest with a count.
- **Use specmark terminology** — findings reference `proposal` / `design` / `tasks` (not "spec" / "plan" / "implementation"). Task references use the `T###` IDs from tasks.md.
- **No false positives to pad the count** — if a category has no findings, omit it; do not invent LOW findings to fill rows.
- **Do not gate apply** — analyze is advisory. The user may run apply with unresolved findings; analyze does not block.
- **Re-runnable** — after propose regenerates artifacts, analyze can be re-run to confirm findings cleared.

**Fluid Workflow Integration**

- May be invoked anytime after `propose` produces artifacts.
- Most useful as a pre-apply gate, but also valid post-apply (before `converge`) to catch drift introduced during implementation.
- Pairs with `converge`: analyze finds proposal↔tasks gaps pre-apply; converge finds tasks↔code gaps post-apply.
