---
name: specmark
description: "Specmark 规格驱动变更。探索、澄清、提案、分析、实施、收敛、归档多阶段 spec-driven 工作流。触发：为变更生成 proposal/design/tasks、实施任务、归档已完成 change、或提到 specmark 工作流。$ARGUMENTS[0] 选子命令，无参列子命令表。"
argument-hint: "[explore|clarify|propose|analyze|apply|converge|archive]"
license: MIT
---

# Specmark 规格驱动变更工作流

通过 `$ARGUMENTS[0]` 选择子命令。每个子命令的完整流程、步骤、Guardrails 在 `references/<子命令>.md`，按需加载。

## 子命令路由

| 参数       | 功能                                                  | 参考                    |
| ---------- | ----------------------------------------------------- | ----------------------- |
| `explore`  | 探索/思考模式（只读，不写应用代码）                   | `references/explore.md` |
| `clarify`  | 结构化澄清，propose 前可选（≤5 高影响问题，8 分类扫描）| `references/clarify.md` |
| `propose`  | 一步生成 proposal + design + tasks 全套产物           | `references/propose.md` |
| `analyze`  | 跨产物一致性分析（只读质量门，propose 后 apply 前）   | `references/analyze.md` |
| `apply`    | 按 tasks.md 实施任务，逐条勾选                        | `references/apply.md`   |
| `converge` | 收敛：apply 完成后对比代码与 spec，append 缺漏任务    | `references/converge.md`|
| `archive`  | 归档已完成变更，含 delta spec 同步评估                | `references/archive.md` |

## 调用示例

- `/specmark propose add-user-auth` — 明确子命令 + 变更名，生成全套产物
- `/specmark clarify add-user-auth` — propose 前澄清模糊点（≤5 问，8 分类扫描）
- `/specmark analyze add-user-auth` — 检查 proposal/design/tasks 一致性（只读质量门）
- `/specmark apply` — 实施 / 继续当前 change
- `/specmark converge` — apply 后对比代码与 spec，append 缺漏任务
- `/specmark` — 无参 → 列出路由表
- 「我还没想好这个功能，先聊聊」 — 自然语言意图 → 确认后进 explore

## 执行流程

**🔴 CHECKPOINT · 🛑 STOP：解析 `$ARGUMENTS[0]` 后、进入子命令流程前，先确认子命令选择正确（尤其自然语言意图需用 AskUserQuestion 工具与用户确认），避免误路由后回滚成本。**

1. 解析 `$ARGUMENTS[0]`：
   - 合法值（`explore`/`clarify`/`propose`/`analyze`/`apply`/`converge`/`archive`）→ 进入步骤 2
   - 缺失或拼写错误（如 `/specmark`、`/specmark foobar`）→ 输出上方路由表，请用户选择后停止
   - 自然语言意图（如「我还没想好」「帮我梳理思路」「探讨方案」）→ 用 **AskUserQuestion 工具**确认是否进入 `explore`（只读思考模式），不自动路由也不直接列表
2. **Read `references/<子命令>.md`**，按其 Steps + Guardrails 执行。
3. specmark 是**纯文档型 skill**，不依赖外部 CLI：所有变更管理操作（创建 change 目录、读取任务状态、归档）通过 AI agent 的文件系统工具（mkdir/Write/Read/Glob/mv）直接操作 `specmark/` 工作目录完成。

## 子命令选用指南

| 用户意图                                    | 子命令     |
| ------------------------------------------- | ---------- |
| "我想做 X / 加个功能" → 生成完整提案        | `propose`  |
| "帮我梳理这个想法 / 探讨方案 / 对比选项"    | `explore`  |
| "需求里有模糊点 / 先问清楚再提案"           | `clarify`  |
| "提案生成后 / 检查产物一致性 / 质量门"      | `analyze`  |
| "开始实施 / 做下一个任务 / 继续这个 change" | `apply`    |
| "实施完了 / 对比代码和 spec / 补漏"         | `converge` |
| "这个 change 做完了 / 归档 / 收尾"          | `archive`  |
| "我还没想好 / 先聊聊"                       | `explore`  |

## 阶段协作链路

```
explore（探索）→ clarify（澄清）→ propose（生成提案）→ analyze（一致性分析）→ apply（实施）→ converge（收敛）→ archive（归档）
```

- `explore` 是只读思考模式，可随时进入；想清楚后用 `clarify`（可选）或 `propose` 落地为变更。
- `clarify` 是 propose 前的可选澄清步骤；需求明确时直接跳过，进入 `propose`。
- `propose` 产出全套产物后，提示运行 `/specmark analyze`（可选质量门）或 `/specmark apply`。
- `analyze` 是 propose 后 apply 前的可选只读质量门；不阻塞 apply。
- `apply` 全部任务完成后，提示先 `/specmark converge` 再 `/specmark archive`。
- `converge` 是 apply 后 archive 前的可选收敛步骤；append-only 追加遗漏任务，再回到 `apply` 关闭。
- 七阶段非强制线性，clarify/analyze/converge 均可按需跳过（见各 references 的 Fluid Workflow Integration）。

## 维护说明

本技能原为 4 个独立顶层技能（`specmark-propose` / `specmark-explore` / `specmark-apply-change` / `specmark-archive-change`），现已扁平合并：各原 `SKILL.md` 去除 frontmatter 后成为 `references/{propose,explore,apply,archive}.md`；跨技能交叉引用已改写为本技能子命令（`/specmark apply`、`/specmark propose`）。技能发现机制只识别 `specmark/SKILL.md`，不独立获取 `references/` 内的流程文档。

## 不要做什么（反例黑名单）

下列反模式会破坏 spec-driven 工作流的可追溯性与一致性，执行任何子命令前对照检查。

| # | 反模式                                                     | 为什么不要做                                                       | 正确做法                                                              |
| - | ---------------------------------------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------- |
| 1 | 在 `explore` 模式写应用代码                                | explore 是只读思考模式；写代码会让"探索"变成"实施"，破坏阶段边界    | 想清楚后退出 explore，用 `propose` 落地变更，再 `apply` 实施          |
| 2 | 跳过 `propose` 直接 `apply`                                | 没有 proposal/design/tasks 就实施，spec 失去追溯依据，converge 失效 | 先 `/specmark propose` 生成全套产物，再 `/specmark apply`             |
| 3 | 修改已归档的 change（`docs/changes/archive/` 下文件）      | 归档是只读历史；改动归档会让 spec 与历史代码脱钩                    | 新建 change 处理后续变更；归档内容只读                                |
| 4 | `apply` 跳过未完成任务直接做下一个                         | 顺序执行是硬约束；跳过会让下游任务依赖缺失                          | 严格按 `tasks.md` 顺序；遇阻则 PAUSE，不跳过                          |
| 5 | `converge` 改写已有任务而非 append                         | append-only 是硬约束；改写会让历史任务不可追溯                      | 仅在 `## Phase N: Convergence` 段追加新任务                           |
| 6 | 在 `tasks.md` 留 `TBD` / `TODO` / "as needed" 等占位符     | 占位符让 apply 中途停滞；任务必须可执行                             | 拆为具体子任务，或写到 `proposal.md` 的 `## NEEDS CLARIFICATION`      |
