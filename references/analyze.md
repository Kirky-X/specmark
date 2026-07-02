# Analyze — 跨产物一致性检查（只读质量门）

`propose` 与 `apply` 之间的可选质量门。读取某变更的 `proposal.md`、`design.md`、`tasks.md`，检测跨产物一致性问题，输出 Markdown 报告。**只读**：analyze 绝不修改任何产物。

**定位**：可选，在 `propose` 之后、`apply` 之前。变更非平凡时使用（如触及 >1 个模块、多步任务、外部集成），值得二次审视。平凡变更跳过。

**输入**：可选指定变更名。若省略，从上下文推断或用 Glob 工具列 `specmark/changes/*/` 目录（子目录名即变更名）。

**Steps**

1. **定位变更及其产物**

   读 `specmark/changes/<name>/tasks.md` 的复选框状态（`- [ ]` 待办 / `- [x]` 完成）确认 `proposal.md`、`design.md`、`tasks.md` 都存在。若任一缺失，输出 CRITICAL 发现（见检测 #6）并用现有内容继续。

2. **完整读取全部三份产物**

   端到端读 `proposal.md`、`design.md`、`tasks.md`。不要略读 —— 跨产物不一致只在三者并持时浮现。

3. **跑 6 个检测 pass**

   每个 pass 扫描全部三份产物并记录发现。每个发现含：检测类型、严重度、位置、描述。

   | # | 检测             | 捕获什么                                                 |
   | - | ---------------- | -------------------------------------------------------- |
   | 1 | Duplication      | 同一需求/任务在两处陈述且有漂移                          |
   | 2 | Ambiguity        | 术语或行为有多重合理解释                                 |
   | 3 | Underdetermined  | 任务无法在无进一步决策下实施                             |
   | 4 | Coverage gap     | proposal/design 中有需求但无对应任务                     |
   | 5 | Inconsistency    | proposal vs design vs tasks 在具体点上互相矛盾           |
   | 6 | Missing artifact | 必需产物缺失（如无 tasks.md、无 design.md）              |

4. **为每个发现分配严重度**

   | 严重度    | 含义                                                                 |
   | --------- | -------------------------------------------------------------------- |
   | CRITICAL  | 阻塞 apply —— 矛盾或缺失产物                                         |
   | HIGH      | 会在 apply 中导致返工 —— 核心需求覆盖缺口                            |
   | MEDIUM    | 歧义或规格不足的任务；apply 中可附注解决                             |
   | LOW       | 装饰性漂移、重复措辞；修复可选                                       |

5. **上限 50 个发现**

   若超过 50 个，保留 50 个最高严重度（CRITICAL → LOW）并追加末行：`... 还有 N 个发现已抑制（修复 CRITICAL/HIGH 后重跑 analyze）`。

6. **输出报告 —— 只读，不写文件**

   把报告打印到对话。**不要**写盘，**不要**编辑任何产物。用户若想应用修复，跑 `propose`（重新生成）或 `converge`（apply 后）。

**输出**

```
## Analyze 报告 — <change-name>

**已读产物：** proposal.md, design.md, tasks.md
**发现：** N (CRITICAL: a | HIGH: b | MEDIUM: c | LOW: d)

| # | 严重度    | 检测             | 位置                  | 发现                                                |
| - | --------- | ---------------- | --------------------- | --------------------------------------------------- |
| 1 | CRITICAL  | Missing artifact | —                     | tasks.md 缺失                                       |
| 2 | HIGH      | Coverage gap     | proposal §2 / tasks   | proposal 有"限流"，无任务实施                       |
| 3 | MEDIUM    | Underdetermined  | tasks T03             | "选一个缓存策略" —— 无决策记录                      |
| 4 | LOW       | Duplication      | design §1 / tasks T01 | 重试策略陈述两次且 backoff 不同                     |

**建议：** `/specmark apply` 前修复 CRITICAL 与 HIGH。MEDIUM/LOW 可在 apply 中就地解决。
```

**Guardrails**

- **只读** —— 绝不写入、编辑或移动任何产物。Analyze 观察；不行动。
- **上限 50 个发现** —— 硬上限。超限 → 保留最高严重度，抑制其余并计数。
- **用 specmark 术语** —— 发现引用 `proposal` / `design` / `tasks`（不是 "spec" / "plan" / "implementation"）。任务引用用 tasks.md 的 `T###` ID。
- **不要凑数** —— 若某类无发现，省略；不要编造 LOW 发现填行。
- **不阻塞 apply** —— analyze 是建议性的。用户可带未解决发现跑 apply；analyze 不阻塞。
- **可重跑** —— propose 重新生成产物后，可重跑 analyze 确认发现已清。

**Fluid Workflow Integration**

- 可在 `propose` 产出产物后任何时候调用。
- 最有用作 apply 前质量门，但 apply 后也有效（converge 前）以捕获实施中引入的漂移。
- 与 `converge` 配对：analyze 找 apply 前的 proposal↔tasks 缺口；converge 找 apply 后的 tasks↔code 缺口。
