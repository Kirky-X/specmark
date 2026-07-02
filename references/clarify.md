# Clarify — Structured clarification before propose

An optional pre-step to `propose`. Triggered when the user's description contains ambiguities that would otherwise force the proposal to guess. Clarify asks a small number of high-impact questions, writes each answer into `proposal.md` under a `## Clarifications` section, then hands off to `propose`.

**Positioning**: Optional, before `propose`. Skip if the request is already concrete. Never a replacement for `explore` (open-ended thinking) — clarify is a focused, bounded Q&A over 8 categories.

**Input**: A user description of the change they want. May be invoked explicitly as `/specmark clarify <name>` or suggested by `propose` when it detects ambiguity.

**Steps**

1. **Scan the description across 8 categories**

   Walk the user's description against the 8-category coverage scan. For each category, decide: *covered*, *ambiguous*, or *missing*. Only categories marked *ambiguous* or *missing* are eligible to produce a question.

   | Category           | What it asks                                                      |
   | ------------------ | ----------------------------------------------------------------- |
   | Functional Scope   | What's in vs. out of scope; explicit non-goals                    |
   | Domain             | Domain-specific rules, entities, invariants                       |
   | UX                 | User-facing flows, error states, feedback                         |
   | NFR                | Performance, availability, durability, security, accessibility    |
   | Integration        | Upstream/downstream systems, contracts, data ownership            |
   | Edge Cases         | Empty input, concurrent access, partial failure, scale ceilings   |
   | Constraints        | Hard constraints: deadline, budget, tech stack, compliance        |
   | Terminology        | Terms whose meaning differs by stakeholder (e.g., "user", "order")|

2. **Select at most 5 high-impact questions**

   - Rank ambiguous/missing categories by impact (a wrong guess blocks implementation → high; a wrong guess is cosmetic → low).
   - Cap at **5 questions**. If more categories remain, fall back to reasonable defaults (see step 4) and note them in the proposal.
   - Each question is either **short-answer** or **multiple-choice**. For multiple-choice, list 2-4 concrete options plus an "other" escape hatch. Never ask open-ended essay questions.

3. **Ask questions one batch via AskUserQuestion tool**

   Batch the ≤5 questions in a single AskUserQuestion call so the user can answer in one pass. Do not interrogate question-by-question.

4. **Apply reasonable defaults silently for non-asked categories**

   Defaults are NOT flagged as assumptions in the proposal — they are the industry baseline. Only deviate when the user explicitly overrides.

   | Category         | Default                                                   |
   | ---------------- | --------------------------------------------------------- |
   | Data retention   | Industry standard for the domain (e.g., 90-day audit log) |
   | Performance      | Web: p95 < 200ms / mobile: p95 < 500ms                    |
   | Availability     | Single-region, business-hours SLO                         |
   | Accessibility    | WCAG 2.1 AA                                               |
   | Logging          | Structured logs, no PII                                   |
   | Error reporting  | Sentry-class: errors + stack, no user data                |

5. **Write each answer into proposal.md as it arrives**

   After the user answers, append to `specmark/changes/<name>/proposal.md`:

   ```markdown
   ## Clarifications

   - **[Functional Scope]** Q: <question text>
     A: <user answer, verbatim or lightly paraphrased>
   - **[NFR]** Q: <question text>
     A: <user answer>
   ```

   Write incrementally — one entry per answered question — not as a single batch at the end. If `proposal.md` does not yet exist, create it with just the `## Clarifications` section; `propose` will fill in the rest.

6. **Hand off to propose**

   Once all answers are recorded, prompt: "Clarifications captured. Run `/specmark propose <name>` to generate the full proposal."

**Output**

```
## Clarification Complete

**Change:** <name>
**Questions asked:** N/5
**Defaults applied:** <list of categories that used defaults>

Captured in `proposal.md` → `## Clarifications`.
Next: `/specmark propose <name>`
```

**Guardrails**

- **Max 5 questions** — hard cap. If you find a 6th, it must be a default.
- **No essay questions** — short-answer or multiple-choice only.
- **Defaults are silent** — do not surface them as "assumptions needing confirmation"; that defeats the purpose.
- **Read-only on existing artifacts** except appending to `proposal.md`'s `## Clarifications` section. Do not touch design.md or tasks.md.
- **Skip entirely if the request is concrete** — clarify is optional, not mandatory. If 0 categories are ambiguous/missing, announce "No clarification needed" and suggest `/specmark propose` directly.
- **Never block propose** — if the user declines to answer, proceed to propose with defaults; do not stall.

**Fluid Workflow Integration**

- May be invoked anytime before `propose`, including after `explore`.
- If `propose` is already in progress and hits ambiguity mid-generation, it may delegate back to `clarify` for one targeted question, then resume.
- Clarify does not consume `explore`'s role: explore is open-ended thinking; clarify is bounded Q&A over the 8 categories.
