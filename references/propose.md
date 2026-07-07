# Propose — 一步创建变更并生成全套产物

提出新变更 —— 创建 change 并一步生成所有产物。

我会创建一个变更，包含产物：

- proposal.md（做什么 & 为什么）
- design.md（怎么做）
- tasks.md（实施步骤）
- specs/（长程变更自动生成 delta spec 文件，见步骤 4c）

准备好实施时，运行 `/specmark apply`。

---

**输入**：用户的请求应包含一个变更名（kebab-case）或对他们想构建什么的描述。

**Steps**

1. **如果未提供明确输入，询问用户想构建什么**

   🔴 CHECKPOINT · 🛑 STOP：在调用 AskUserQuestion 前确认确实缺乏足够信息（变更名或描述均缺失），不要在已有足够上下文时仍反复追问。

   > **输入：** `$ARGUMENTS`（可能含变更名或描述）
   > **输出：** kebab-case 变更名 + 变更描述（写入内存，步骤 2-4 使用）

   使用 **AskUserQuestion 工具**（开放式，无预设选项）问：

   > "你想做什么变更？描述你想构建或修复什么。"

   从他们的描述中派生一个 kebab-case 名字（如 "add user authentication" → `add-user-auth`）。

   **重要**：在理解用户想构建什么之前不要继续。

2. **创建变更目录**

   > **输入：** 变更名 `<name>`
   > **输出：** `specmark/changes/<name>/` 目录创建成功

   用 **mkdir** 操作创建 `specmark/changes/<name>/`。目录本身就是变更记录 —— 不使用单独的配置文件。

3. **检查现有进度**

   > **输入：** 变更名 `<name>`
   > **输出：** 进度状态（全新 / 继续中 + 已完成产物列表）

   读 `specmark/changes/<name>/` 下的全部产物（`proposal.md` / `design.md` / `tasks.md`）并检查各自状态以了解已完成什么。若三份产物均不存在，视为全新变更。若 `proposal.md` 已存在且含 `## Clarifications` 节（由 `clarify` 写入），步骤 4a 创建/更新 `proposal.md` 时必须保留该节，不得覆盖。

4. **按序创建产物直到 apply-ready**

   > **输入：** 变更名 `<name>` + 变更描述 + 进度状态
   > **输出：** `proposal.md` + `design.md` + `tasks.md` + `specs/`（长程）写入 `specmark/changes/<name>/`

   用 **TodoWrite 工具**跟踪产物进度。

   specmark 提供自己的产物模板 —— `proposal.md` / `design.md` / `tasks.md`（以及长程变更的 `specs/`）—— 定义在下方的 **产物模板** 与 **任务编写标准** 章节。不查询任何外部 CLI 获取指令。

   按依赖顺序循环产物（无待处理依赖的产物优先）：

   a. **对每个 `ready`（依赖已满足）的产物**：
   - 使用 specmark 产物模板（结构定义在下方与 `references/`）作为输出文件结构
   - 创建新产物前读已完成的依赖文件（如写 `tasks.md` 前读 `proposal.md` 和 `design.md`）
   - 在 `specmark/changes/<name>/<artifact>.md` 写入产物文件
   - 显示简短进度："Created <artifact-id>"

   b. **继续直到所有必需产物完成**
   - 每创建一个产物后，重读 `specmark/changes/<name>/tasks.md` 复选框状态确认进度
   - 当 `proposal.md`、`design.md`、`tasks.md` 都存在且 `tasks.md` 列出每个已提交任务时停止

   c. **长程变更自动生成 delta spec**（在 tasks.md 完成后评估）

      **复杂度评估**：tasks.md 创建完成后，评估变更是否为长程任务。满足以下任一条件即判定为长程：
      - tasks.md 中任务数 ≥ 5
      - 变更跨 ≥ 3 个独立模块/目录
      - proposal.md 描述涉及多个能力域或子系统

      **长程变更**：在 `specmark/changes/<name>/specs/` 下为每个受影响的能力域创建 delta spec 文件（`specs/<capability>/spec.md`）。每个 delta spec 描述该能力域在此变更中的**具体需求**——从 proposal.md 的 Scope/Requirements 和 design.md 的 Decision 中提取，聚焦可验证的行为规格（输入→预期输出、边界条件、错误行为）。

      **短程变更**（任务数 < 5 且影响范围小）：跳过 spec 生成。proposal.md + design.md 已提供足够上下文。

      Delta spec 模板见下方 **specs/ 骨架**。完成后显示："Created specs/<capability>/spec.md"

   d. **如果某产物需要用户输入**（上下文不清）：
   - 🔴 CHECKPOINT · 🛑 STOP：仅在真正阻塞时才打断用户问澄清；能基于已有 proposal/design 做合理决策的就继续，避免频繁中断。
   - 用 **AskUserQuestion 工具**澄清
   - 然后继续创建

5. **显示最终状态**

   > **输入：** `specmark/changes/<name>/tasks.md` 复选框状态
   > **输出：** 进度报告 + 自动衔接 analyze

   读 `specmark/changes/<name>/tasks.md` 并报告复选框进度。

**输出**

完成所有产物后，总结：

- 变更名与位置
- 创建的产物列表及简短描述（含 specs/ 下的 delta spec 文件，若长程变更）
- 自动衔接 analyze："已就绪。自动执行一致性分析…"

analyze 完成后，展示结果并自动衔接下一步：
- 无 CRITICAL/HIGH → "分析通过。自动开始实施…" → 进入 apply
- 有 CRITICAL/HIGH → "发现 N 个问题。" → 展示报告 → 用 **AskUserQuestion 工具**问用户：修复后继续 / 直接开始实施 / 先看看报告

**Guardrails**

- 创建实施所需的全部产物（proposal.md、design.md、tasks.md），遵循下方 **产物模板** 与 **任务编写标准** 章节定义的模板结构
- **模板指令是约束，不是文件内容** —— 不要把模板注释、示例或占位标记复制进产物；它们指导你写什么，但绝不应出现在输出中
- 长程变更（任务数 ≥ 5、跨 ≥ 3 模块、或 proposal.md 描述涉及多个能力域或子系统）额外生成 `specs/<capability>/spec.md`；短程变更跳过
- 创建新产物前总是读依赖产物（如写 `tasks.md` 前读 `proposal.md` 和 `design.md`）
- 如果上下文严重不清，问用户 —— 但优先做合理决策保持动量
- 如果同名变更已存在，问用户想继续它还是新建一个
- 写入后、进入下一个前验证每个产物文件存在
- **按顺序排列任务** —— 在 `tasks.md` 中按执行/依赖顺序列任务。下游 `/specmark apply` 强制严格顺序执行（不跳过），所以排列时让每个任务能在下一个开始前完成

---

## 产物模板（Artifact Templates）

以下骨架是 specmark 产物的强制结构。创建产物时用对应骨架填充，不要自创章节。

### proposal.md 骨架

```markdown
# <change-name>

## Motivation
<为什么做这个变更？解决什么问题/抓住什么机会。1-2 段，指向具体痛点或需求来源>

## Scope
<这个变更覆盖什么。列具体能力/模块/行为。与 Non-Goals 对应>

## Non-Goals
<明确不做什么。防止范围蔓延。每条写明为什么排除>

## Clarifications
<来自 /specmark clarify 的问答记录。若无则省略本节>

- **[<category>]** Q: <问题>
  A: <用户回答>

## NEEDS CLARIFICATION
<仅当 propose 自检后仍有无法转为具体任务的需求时才写。硬上限 3 条>

- **[<category>]** <不清楚什么> — <为什么阻塞任务> — <用户不回答时的默认值>
```

### design.md 骨架

```markdown
# Design — <change-name>

## Context
<做这个决策时的背景：现有架构、约束、相关历史决策。给读者足够上下文理解为什么这么决定>

## Decision
<采用了什么方案。具体到可实施：数据结构、接口签名、模块划分、关键算法>

## Alternatives Considered
<考虑过但没采用的方案。每个写明：方案是什么、为什么没选（权衡）>

## Consequences
<这个决策的后果：正面影响、负面影响、技术债、需后续跟进项>
```

### tasks.md 骨架

tasks.md 用 **任务编写标准** 的 5 元素格式，按执行顺序列出。骨架：

```markdown
# Tasks — <change-name>

- [ ] [T001] [P0] <描述，含文件路径>
- [ ] [T002] [P1] <描述，含文件路径>
...

## Phase N: Convergence
<仅由 /specmark converge 追加，propose 不写本节>
```

### specs/ 骨架（长程变更）

长程变更在 `specmark/changes/<name>/specs/<capability>/spec.md` 创建 delta spec。每个文件对应一个能力域，描述该能力域在此变更中的具体可验证需求。

```markdown
# Spec — <capability>

> Delta spec for change `<change-name>`. 覆盖此变更引入/修改的该能力域需求。

## Requirements

### R-<capability>-001: <需求名>
<可验证的行为描述：输入→预期输出、边界条件、错误行为>

**验收标准：**
- <具体可测试条件>

### R-<capability>-002: <需求名>
<可验证的行为描述>

**验收标准：**
- <具体可测试条件>

## Constraints
<该能力域的约束条件（性能、安全、兼容性等）>

## Out of Scope
<此变更明确不覆盖的该能力域范围>
```

**编写要求：**
- 从 proposal.md 的 Scope 和 design.md 的 Decision 中提取需求，转化为可验证规格
- 每条 Requirement 必须有明确的验收标准，apply 和 converge 可直接对照检查
- 不复制 proposal/design 原文；提炼为精确的行为约束
- capability 命名用 kebab-case，与受影响的模块/子系统对应

---

## 任务编写标准

以下标准在编写 `tasks.md` 时适用。它们是强制性的；`apply` 和 `converge` 都假设任务符合它们。

### 1. 任务格式 — 5 元素

每个任务行用这个精确形状：

```
- [ ] [T###] [P?] [Story?] Description with file path
```

| 元素          | 必需 | 含义                                                              |
| ------------- | ---- | ----------------------------------------------------------------- |
| `- [ ]`       | 是   | 复选框；完成时由 `apply` 翻转为 `- [x]`                          |
| `[T###]`      | 是   | 零填充稳定 ID（T001、T002...）。永不重排已有 ID                   |
| `[P?]`        | 是   | 优先级：P0（阻塞）/ P1（必须）/ P2（可选）。被 converge 使用      |
| `[Story?]`    | 可选 | 如果变更对应 backlog story，填 story ID                           |
| Description   | 是   | 祈使句、具体、**必须包含被改动的文件路径**                        |

示例：

```
- [ ] [T003] [P1] [AUTH-12] Add rate-limit middleware to src/auth/login.ts (10 req/min/IP)
```

没有文件路径的任务几乎总是规格不足 —— 修描述，不要放宽规则。

### 2. 禁止占位符 — 硬规则

任务必须按所写即可实施，不延迟任何决策。以下措辞在任务描述中**禁止**：

- `TBD`、`TODO`、`FIXME`、`???`、`<...>`
- "add appropriate error handling"（什么算 appropriate？）
- "handle edge cases"（哪些 case？）
- "similar to Task N"（写实际步骤；引用会漂移）
- "write tests for the above"（说明测试断言什么行为）
- "as needed" / "if relevant" / "where appropriate"

如果你写不出具体行为，任务就是规格不足 —— 要么拆成具体子任务，要么把开放问题路由到 `## NEEDS CLARIFICATION`（见下）。

### 3. 小粒度 TDD 颗粒度

每个任务应代表 **2-5 分钟的专注工作**，不是多小时大工程。如果任务会更长，拆分。任何产代码任务的首选形状是 **TDD 五步循环**，编码为一个带五子项的任务或五个连续任务：

1. **Red** — 写一个失败测试钉住期望行为
2. **Green** — 写最少代码让测试通过
3. **Refactor** — 不改行为地改进结构
4. **Commit** — `git commit -m "feat(<area>): <description>"`
5. **Verify** — 跑受影响测试套件；确认 green

颗粒度测试：如果你不能用一句话说出单个文件和单个行为变更，任务就太大。

### 4. 自检 — 完成前三项检查

起草所有任务后，在宣布变更 apply-ready 前跑这三项检查。失败必须在交给 `apply` 前修复。

| 检查              | 验证什么                                                                  |
| ----------------- | ------------------------------------------------------------------------- |
| **Spec 覆盖**     | `proposal.md` 中每个需求与 `design.md` 中每个决策都映射到 ≥1 任务。若存在 `specs/`，每条 delta spec Requirement 也必须映射到 ≥1 任务。未映射需求去 NEEDS CLARIFICATION 或加任务。 |
| **占位符扫描**    | grep tasks.md 找 §2 中的禁用短语。要求零匹配。                            |
| **类型一致**      | 任务 ID 零填充且唯一；优先级取自 {P0,P1,P2}；描述中文件路径指向已存在或更早任务会创建的文件。 |

### 5. NEEDS CLARIFICATION — 有界 bailout

如果自检后仍有需求无法转为具体任务，记录到 `proposal.md` 底部的 `## NEEDS CLARIFICATION` 节（不是 `tasks.md` —— 任务是承诺，澄清是问题）。

- **硬上限：3 条。** 如果有 4+，先跑 `/specmark clarify` 再回来。
- **按影响排序**，高的在前：`scope` > `security/privacy` > `UX` > `technical`。范围歧义比技术歧义阻塞更多下游工作。
- **每条格式**：
  ```
  - **[<category>]** <不清楚什么> — <为什么阻塞任务> — <用户不回答时的默认值>
  ```
- `apply` 遇到与当前任务相关的 NEEDS CLARIFICATION 项时会暂停并提示用户；不静默选默认值。

**交接说明**：propose 完成时，自动进入 `analyze` 执行一致性质量门。analyze 完成后再衔接 `apply` 或提示用户选择。
