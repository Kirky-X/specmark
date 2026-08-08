---
name: specmark
description: "规格驱动变更工作流，八阶段(explore/clarify/propose/analyze/apply/converge/archive/status)。触发：生成 proposal/design/tasks、实施任务、归档 change、查看状态、提到 specmark 工作流。"
argument-hint: "[explore|clarify|propose|analyze|apply|converge|archive|status]"
license: MIT
---

# Specmark 规格驱动变更工作流

通过 `$ARGUMENTS[0]` 选择子命令。每个子命令的完整流程、步骤、Guardrails 在 `references/<子命令>.md`，按需加载。

## 子命令路由

| 参数       | 功能                                                                   | 参考                     |
| ---------- | ---------------------------------------------------------------------- | ------------------------ |
| `explore`  | 探索/思考模式（只读，不写应用代码）                                    | `references/explore.md`  |
| `clarify`  | 结构化澄清，自动链 explore→clarify 衔接点（≤5 高影响问题，8 分类扫描） | `references/clarify.md`  |
| `propose`  | 一步生成 proposal + design + tasks 全套产物（长程变更含 delta spec）   | `references/propose.md`  |
| `analyze`  | 跨产物一致性分析，自动链 propose→analyze 衔接点（只读质量门）          | `references/analyze.md`  |
| `apply`    | 按 tasks.md 实施任务，逐条勾选                                         | `references/apply.md`    |
| `converge` | 收敛：自动链 apply→converge 衔接点，对比交付物与 spec，append 缺漏任务   | `references/converge.md` |
| `archive`  | 归档已完成变更（`--sync` 启用 delta spec 同步到主 specs）              | `references/archive.md`  |
| `status`   | 只读查询活动变更与历史归档概览                                          | `references/status.md`   |

**Flags 速记**：

- `apply --auto-commit`：每任务完成后自动 `git commit`（默认关闭，不破现有行为；详见 `references/apply.md`）。
- `archive --sync`：归档时把 delta spec 同步到 `specmark/specs/<cap>/spec.md`（由 `scripts/merge_delta_spec.py` 确定性合并，不启动 LLM；详见 `references/archive.md`）。
- **归档只读**：`specmark/archive/` 由 `scripts/archive_change.sh` 维护 `.readonly` 哨兵 + change 级 flock + commit SHA 锚定；既有归档条目禁止修改，只允许追加。
- **归档预览**：`archive --dry-run` 预览归档结果而不执行实际操作（详见 `references/archive.md`）。
- **确定性工具（必须调用，禁止手动替代）**：

  | 脚本 | 用途 | 何时调用 | 子命令 |
  |------|------|----------|--------|
  | `scripts/check_phase.sh` | 阶段完成确定性判定 | propose/apply/converge/archive 各阶段 | `complexity` / `tasks` / `converge-readiness` / `archive-readiness` / `artifacts` |
  | `scripts/status.sh` | 全局状态查询 | status 子命令 | `--json` 可选 |
  | `scripts/check_refs.py` | 跨文件引用一致性 lint | analyze 阶段、修改 reference 文件后 | `--root` / `--json` / `--verbose` |
  | `scripts/archive_change.sh` | 归档执行器（含 flock + 只读强制） | archive 子命令步骤 5 | `--sync` / `--date` / `--dry-run` |
  | `scripts/merge_delta_spec.py` | delta spec 确定性合并 | archive --sync 时由 archive_change.sh 自动调用 | `--main` / `--delta` / `--out` / `--dry-run` |

  > **规则 3 对齐**：上述脚本覆盖的判定逻辑（任务计数、复杂度评估、归档就绪、引用一致性）属于确定性逻辑，禁止 agent 手动读文件后自行计算。

## Domain（领域类型）

每个 specmark 变更都属于一个领域（domain）。domain 决定任务格式、apply 执行策略和 converge 验证方式。

| domain | 含义 | 交付物标识示例 |
|--------|------|----------------|
| `code` | 软件开发（默认） | `src/auth/login.ts` |
| `doc` | 文档/内容创作 | `docs/chapter-3.md` |
| `event` | 活动策划/执行 | `venue-contract-signed` |
| `design` | 设计项目 | `designs/homepage-v2.fig` |
| `research` | 研究项目 | `research/market-analysis.md` |
| `general` | 通用 | `stakeholder-approval` |

**声明方式**：在 proposal.md 头部加 `<!-- domain: <type> -->`（HTML 注释，不影响渲染）。

**自动推断规则**（无显式声明时）：
- 任务描述含源码扩展名（`.ts/.py/.go/.rs/.java/.js/.jsx/.tsx/.c/.cpp/.h`）→ `code`
- 任务描述含 `→ <path>` 且目标为 `.md/.txt/.docx` → `doc`
- 任务描述含 `→ <path>` 且目标为 `.fig/.sketch/.xd` → `design`
- 任务描述无可验证文件引用 → `general`

默认 domain 为 `code`（向后兼容）。

## 调用示例

```mermaid
flowchart LR
    subgraph 入口
        U1["/specmark explore"]
        U2["/specmark propose <name>"]
        U3["/specmark apply"]
        U4["/specmark"]
    end

    U1 --> E[/"explore → clarify → propose\n→ analyze → apply → converge"/]
    U2 --> P[/"propose → analyze\n→ apply → converge"/]
    U3 --> A[/"apply → converge"/]
    U4 --> R["输出路由表\n等待用户选择"]

    E --> ASK{{"提问下一步"}}
    P --> ASK
    A --> ASK

    ASK -->|"归档"| AR[/"archive"/]
    ASK -->|"新变更"| NP[/"propose"/]
    ASK -->|"探索"| NE[/"explore"/]
```

## 执行流程

**🔴 CHECKPOINT · 🛑 STOP：解析 `$ARGUMENTS[0]` 后、进入子命令流程前，先确认子命令选择正确（尤其自然语言意图需用 AskUserQuestion 工具与用户确认），避免误路由后回滚成本。**

1. 解析 `$ARGUMENTS[0]`：
   - 合法值（`explore`/`clarify`/`propose`/`analyze`/`apply`/`converge`/`archive`/`status`）→ 进入步骤 2
   - 缺失或拼写错误（如 `/specmark`、`/specmark foobar`）→ 输出上方路由表，请用户选择后停止
   - 自然语言意图（如「我还没想好」「帮我梳理思路」「探讨方案」）→ 用 **AskUserQuestion 工具**确认是否进入 `explore`（只读思考模式），不自动路由也不直接列表
   - `status` → Read `references/status.md`，运行 `scripts/status.sh` 展示状态后停止（不进入自动链）
2. **Read `references/<子命令>.md`**，按其 Steps + Guardrails 执行。
3. 所有变更管理操作（创建 change 目录、读取任务状态、归档）通过 AI agent 的文件系统工具（mkdir/Write/Read/Glob/mv）直接操作 `specmark/` 工作目录完成。**阶段判定与状态计算必须调用 `scripts/` 下的确定性脚本**，不由 agent 手动读文件后计算。各阶段脚本调用点：

   | 阶段 | 必须调用的脚本 |
   |------|------------------|
   | propose | `scripts/check_phase.sh complexity <name>`（产物完成后评估复杂度） |
   | apply | `scripts/check_phase.sh tasks <name>`（检查状态 + 显示进度） |
   | converge | `scripts/check_phase.sh converge-readiness <name>`（验证 apply 完成） |
   | archive | `scripts/check_phase.sh artifacts <name>` + `scripts/check_phase.sh archive-readiness <name>` + `scripts/archive_change.sh`（执行归档） |
   | analyze | `scripts/check_refs.py --root <project-root>`（跨文件引用一致性） |
   | status | `scripts/status.sh`（全局状态查询） |

## 子命令选用指南

| 用户意图                                    | 子命令     |
| ------------------------------------------- | ---------- |
| "我想做 X / 加个功能" → 生成完整提案        | `propose`  |
| "帮我梳理这个想法 / 探讨方案 / 对比选项"    | `explore`  |
| "需求里有模糊点 / 先问清楚再提案"           | `clarify`  |
| "提案生成后 / 检查产物一致性 / 质量门"      | `analyze`  |
| "开始实施 / 做下一个任务 / 继续这个 change" | `apply`    |
| "实施完了 / 对比交付物和 spec / 补漏"         | `converge` |
| "这个 change 做完了 / 归档 / 收尾"          | `archive`  |
| "当前状态 / 有哪些变更 / 进度如何"             | `status`   |
| "我还没想好 / 先聊聊"                       | `explore`  |

> **注意：** 自动链生效时，输入 `explore` 会依次自动执行 clarify → propose → analyze → apply → converge → 提问下一步。用户可在任意阶段发出新指令中断链路。

## 阶段协作链路

```mermaid
flowchart LR
    E[/"explore"/] --> C[/"clarify"/]
    C --> P[/"propose"/]
    P --> A[/"analyze"/]
    A --> Ap[/"apply"/]
    Ap --> Co[/"converge"/]
    Co --> Ar[/"archive"/]

    style E fill:#e8f5e9,stroke:#4caf50
    style C fill:#e3f2fd,stroke:#2196f3
    style P fill:#fff3e0,stroke:#ff9800
    style A fill:#fce4ec,stroke:#e91e63
    style Ap fill:#f3e5f5,stroke:#9c27b0
    style Co fill:#e0f2f1,stroke:#009688
    style Ar fill:#fafafa,stroke:#9e9e9e
```

> 非强制线性：clarify / analyze / converge 可按需跳过。自动链中见下方衔接规则。

## 自动执行链

阶段之间存在自动衔接。每个阶段完成时，自动启动下一个阶段，**不等待用户确认**：

```mermaid
flowchart TD
    E[/"explore"/] -->|"有明确想法"| C[/"clarify"/]
    E -->|"无明确方向"| UQ{{"AskUserQuestion"}}
    C -->|"0 歧义，跳过"| P
    C -->|"≤5 问题已答"| P[/"propose"/]
    P --> D["创建 proposal + design + tasks + specs(长程)"]
    D --> An[/"analyze"/]
    An -->|"无 CRITICAL/HIGH"| Ap[/"apply"/]
    An -->|"有 CRITICAL/HIGH"| CR{{"AskUserQuestion\n修复/跳过/查看"}}
    CR --> Ap
    Ap -->|"全部 - [x]"| Co[/"converge"/]
    Ap -->|"PAUSE（阻塞）"| WAIT{{"等待用户决策"}}
    Co -->|"无追加任务"| ASK{{"AskUserQuestion\n归档/新变更/探索/其他"}}
    Co -->|"追加任务 → 回到 apply\n（循环 ≤ 3 次）"| Ap
    Co -->|"循环 > 3 次"| STOP["硬规则强制停止\n展示 3 轮摘要"]

    UQ -->|"用户选择"| E2["进入对应阶段"]
    CR -->|"修复后继续"| P
    CR -->|"跳过直接实施"| Ap
    WAIT -->|"用户决策"| Ap
    ASK -->|"归档"| Ar[/"archive"/]
    ASK -->|"新变更"| P2[/"propose"/]
    ASK -->|"继续探索"| E3[/"explore"/]

    style E fill:#e8f5e9,stroke:#4caf50
    style C fill:#e3f2fd,stroke:#2196f3
    style P fill:#fff3e0,stroke:#ff9800
    style An fill:#fce4ec,stroke:#e91e63
    style Ap fill:#f3e5f5,stroke:#9c27b0
    style Co fill:#e0f2f1,stroke:#009688
    style Ar fill:#fafafa,stroke:#9e9e9e
    style CR fill:#fff9c4,stroke:#fbc02d
    style STOP fill:#ffebee,stroke:#f44336
```

**手动调用仍有效。** 自动链不阻止用户显式调用任一子命令（如 `/specmark analyze` 独立运行）。

**自动链中的阶段仍遵循各自的 Guardrails。** 例如 clarify 发现 0 个歧义时跳过（announce"无需澄清"后继续 propose）；analyze 无 CRITICAL/HIGH 发现时报告通过后继续。

### 自动链失败模式

| 阶段              | 失败条件                                                 | 处理                                                                                         |
| ----------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| explore → clarify | explore 未产出明确想法（开放式讨论、多方向并存）         | 不自动进 clarify；用 AskUserQuestion 问用户下一步                                            |
| clarify → propose | clarify 仍有 4+ 未答分类                                 | 不自动进 propose；展示已捕获的澄清 + 未答分类，用 AskUserQuestion 补问或用默认值继续         |
| propose → analyze | propose 产物创建失败（如目录写入错误）                   | 报错停止，不进 analyze；提示用户检查权限或路径                                               |
| analyze → apply   | analyze 发现 CRITICAL 级问题                             | 暂停自动链；展示报告；用 AskUserQuestion 问：修复后继续 / 跳过直接实施 / 查看报告            |
| apply → converge  | apply 有任务被 PAUSE（阻塞/不清）                        | 不自动进 converge；展示暂停原因，等待用户决策                                                |
| converge → 提问   | converge 追加任务后回到 apply，循环 **> 3 次**仍有新缺口 | **硬规则强制停止**；展示 3 轮摘要；用 AskUserQuestion 问用户：接受当前状态 / 手动介入 / 暂停 |
| 任意阶段          | 用户在阶段执行中发出新指令                               | 立即停止当前阶段，响应用户新指令                                                             |

**链路终止后：** converge 完成后（或 apply 后无需 converge 时），主动向用户提问下一步操作，不结束对话。可用选项：

- 归档此变更（`/specmark archive`）
- 开始新变更
- 继续探索其他方向
- 其他操作

**用户可随时中断自动链。** 阶段执行中用户发出新指令时，立即停止当前阶段并响应用户。

### 自动链短路（复杂度自适应）

完整七阶段适合复杂变更，但对简单变更（单文件、<3 行改动、typo 修复）过重。自动链启动时做复杂度快评，按需缩短链路：

| 复杂度 | 判定条件 | 链路 |
|---------|----------|------|
| **简单** | 单文件、任务数 ≤2、无跨模块影响 | `propose` → `apply`（跳过 clarify/analyze/converge） |
| **中等** | 多文件但任务数 <5、单模块内 | `propose` → `analyze` → `apply` → `converge`（跳过 clarify） |
| **复杂** | 任务数 ≥5 或跨 ≥3 模块或多能力域 | 完整七阶段 |

**判定由 `scripts/check_phase.sh complexity <name>` 确定性执行**（检查任务数、模块数、proposal scope 宽度）。

**用户可显式覆盖**：如「我知道这很简单，但走完整流程」→ 强制完整链路；或「这个很复杂但直接做」→ 强制短路。

**短路不跳过 apply 的关键审查**（`references/apply.md` 实施前 4 项检查始终执行）。

## 不要做什么（反例黑名单）

下列反模式会破坏 spec-driven 工作流的可追溯性与一致性，执行任何子命令前对照检查。

| #   | 反模式                                                 | 为什么不要做                                                        | 正确做法                                                                           |
| --- | ------------------------------------------------------ | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 1   | 在 `explore` 模式写应用代码                            | explore 是只读思考模式；写代码会让"探索"变成"实施"，破坏阶段边界    | 想清楚后退出 explore，用 `propose` 落地变更，再 `apply` 实施                       |
| 2   | 跳过 `propose` 直接 `apply`                            | 没有 proposal/design/tasks 就实施，spec 失去追溯依据，converge 失效 | 先 `/specmark propose` 生成全套产物（长程变更含 delta spec），再 `/specmark apply` |
| 3   | 修改已归档的 change（`specmark/archive/` 下文件）      | 归档是只读历史；改动归档会让 spec 与历史代码脱钩                    | 新建 change 处理后续变更；归档内容只读                                             |
| 4   | `apply` 跳过未完成任务直接做下一个                     | 顺序执行是硬约束；跳过会让下游任务依赖缺失                          | 严格按 `tasks.md` 顺序；遇阻则 PAUSE，不跳过                                       |
| 5   | `converge` 改写已有任务而非 append                     | append-only 是硬约束；改写会让历史任务不可追溯                      | 仅在 `## Phase N: Convergence` 段追加新任务                                        |
| 6   | 在 `tasks.md` 留 `TBD` / `TODO` / "as needed" 等占位符 | 占位符让 apply 中途停滞；任务必须可执行                             | 拆为具体子任务，或写到 `proposal.md` 的 `## NEEDS CLARIFICATION`                   |
| 7   | 手动读文件计算任务数/复杂度/归档就绪状态              | 违反规则 3（确定性逻辑禁止交给模型）；agent 计数可能出错          | 调用 `scripts/check_phase.sh` 对应子命令获取 JSON 结果                            |
| 8   | 非 coding 场景用 code 域格式写任务                     | 交付物标识格式不匹配导致 apply 无法执行、converge 无法对账        | propose 时声明 `<!-- domain: <type> -->`，用对应域的交付物标识格式（见 propose.md） |
