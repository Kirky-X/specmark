# Apply — 实施某 specmark 变更的任务

实施某 specmark 变更的任务。

**输入**：可选指定变更名。若省略，检查能否从对话上下文推断。若模糊或歧义，**必须**提示用户选择可用变更。

**Steps**

1. **选择变更**

   若提供名字，用它。否则：
   - 用户提到某变更时从上下文推断
   - 只有一个活动变更时自动选
   - 若歧义，用 **Glob 工具**列 `specmark/changes/*/` 目录并用 **AskUserQuestion 工具**让用户选

   总是宣布："使用变更：<name>" 及如何覆盖（如 `/specmark apply <other>`）。

2. **检查状态以理解 schema**

   读 `specmark/changes/<name>/tasks.md` 并检查复选框状态（`- [ ]` 未完成 / `- [x]` 完成）以了解进度。

   这告诉你：
   - `schemaName`：使用的工作流（通常 "spec-driven"）
   - 哪个产物含任务（spec-driven 通常 `tasks.md`）

3. **读取 apply 上下文**

   读 `specmark/changes/<name>/` 下的产物 —— `proposal.md`、`design.md`、`tasks.md` —— 作为实施上下文。

   这给你：
   - `contextFiles`：变更目录中的产物文件（proposal/design/tasks，加任何 `specs/` delta）
   - 进度（`tasks.md` 中 `- [ ]` vs `- [x]` 计数：total/complete/remaining）
   - 带状态的任务列表
   - 当前状态指引

   **处理状态：**
   - 若产物缺失（如无 `tasks.md`）：显示消息，建议先用 `/specmark propose` 创建缺失产物
   - 若所有任务已 `- [x]`：祝贺，建议归档
   - 否则：继续实施

4. **读上下文文件**

   读 specmark 变更目录（`specmark/changes/<name>/`）中每个产物文件。
   文件取决于所用 schema：
   - **spec-driven**：proposal、specs、design、tasks
   - 其他 schema：遵循 specmark 变更目录的 contextFiles

5. **显示当前进度**

   显示：
   - 使用 schema
   - 进度："N/M 任务完成"
   - 剩余任务概览
   - 当前状态指引

6. **实施任务（循环直到完成或阻塞）**

   **严格顺序 —— 不跳过。** 按 `tasks.md` 中出现的精确顺序处理任务。任务 N+1 仅在任务 N 标记 `- [x]` 后才能开始。当较早任务仍 `- [ ]` 时绝不跳到更晚任务 —— 即使更晚任务看起来更易、能解锁他人、或更有趣。离开任务 `- [ ]` 的唯一允许理由是真正的阻塞，此时你 PAUSE（见下）—— 不跳过。

   按顺序对每个任务：
   - 显示正在做哪个任务（如 "任务 3/7：<描述>"）
   - 做所需代码改动
   - 保持改动最小且聚焦于那一项任务
   - **立即**在任务文件中标记完成：`- [ ]` → `- [x]`
   - 然后才前进到下一个任务

   **暂停条件：**
   - 任务不清 → 请求澄清。判定"不清"的启发式（满足任一即暂停）：
     - 任务描述无文件路径（无处下手）
     - 任务描述含禁用短语（TBD / TODO / FIXME / ??? / "as needed" / "if relevant" / "where appropriate"）
     - 任务描述 <10 字（规格不足）
     - 任务描述无可验证的完成标准（"做完了"无法判定）
   - 实施暴露设计问题 → 建议更新产物
   - 遇错误或阻塞 → 报告并等待指引
   - 用户打断

7. **完成或暂停时显示状态**

   显示：
   - 本次会话完成的任务
   - 总体进度："N/M 任务完成"
   - 若全部完成：建议归档
   - 若暂停：解释原因并等待指引

**实施中输出**

```
## 实施中：<change-name> (schema: <schema-name>)

正在做任务 3/7：<任务描述>
[...实施中...]
✓ 任务完成

正在做任务 4/7：<任务描述>
[...实施中...]
✓ 任务完成
```

**完成时输出**

```
## 实施完成

**变更：** <change-name>
**Schema：** <schema-name>
**进度：** 7/7 任务完成 ✓

### 本次会话完成
- [x] 任务 1
- [x] 任务 2
...

所有任务完成！可归档此变更。
```

**暂停时输出（遇问题）**

```
## 实施暂停

**变更：** <change-name>
**Schema：** <schema-name>
**进度：** 4/7 任务完成

### 遇到问题
<问题描述>

**选项：**
1. <选项 1>
2. <选项 2>
3. 其他方法

你想怎么做？
```

**Guardrails**

- **不跳过任务** —— 按 `tasks.md` 顺序执行；任务仅在前一个 `- [x]` 后才能开始。若更晚任务看起来诱人或似能解锁他人，先完成当前。留任务未完成去前进绝不允许 —— 只有真正阻塞才暂停（见下）
- 持续推进任务直到完成或阻塞
- 开始前总读上下文文件（来自 apply 指令输出）
- 若任务歧义，实施前暂停并问
- 若实施暴露问题，暂停并建议产物更新
- 保持代码改动最小且限定于每项任务
- 完成每个任务后立即更新复选框
- 遇错误、阻塞或不清需求时暂停 —— 不猜
- 用 specmark 变更目录的 contextFiles，不假设特定文件名

---

## 实施前关键审查

**🔴 CHECKPOINT · 🛑 STOP：进入实施循环（步骤 6）前必须完成本节 4 项检查。任一项失败则停在 apply、不进入循环，先建议修复。这是 30 秒 sanity check，在写任何代码前廉价地捕获问题。**

在步骤 5（显示当前进度）之后、步骤 6（实施任务循环）**之前**，对 `tasks.md` 做关键审查。

**检查（进入循环前全部必须通过）：**

1. **占位符扫描** —— grep `tasks.md` 找 `propose.md` §2 定义的禁用短语（TBD / TODO / FIXME / "add appropriate error handling" / "handle edge cases" / "similar to Task N" / "write tests for the above" / "as needed" / "if relevant" / "where appropriate"）。要求零匹配。
2. **文件路径存在性** —— 每个任务描述含至少一个文件路径。无路径的任务规格不足，会导致实施中途停滞。
3. **隐藏依赖检查** —— 对每个任务 N，验证任务 N+1 所需确实由任务 N（或更早）产出。顺序执行意味着缺失依赖阻塞整条链。
4. **NEEDS CLARIFICATION 扫描** —— 读 `proposal.md` 找 `## NEEDS CLARIFICATION` 节。若任一项影响早期任务，**现在**暴露给用户，在开始前，而非实施中途停滞。

**失败时：**

- 若发现占位符或缺失路径 → 建议 `/specmark propose` 修 `tasks.md` 后再 apply。不静默自己修任务；那是 propose 的职责。
- 若发现隐藏依赖 → 建议通过 `/specmark propose` 重排或拆分任务。
- 若 NEEDS CLARIFICATION 项阻塞 → 提示用户解决（或接受记录的默认值）后进入循环。

**成功时：** 宣布"关键审查通过"并前进到步骤 6。

## Git Worktree 隔离（非平凡变更推荐）

对触及 **≥3 个文件**或跨多次会话的变更，考虑在步骤 6 前用 git worktree 隔离实施：

```bash
git worktree add ../<change-name>-worktree
cd ../<change-name>-worktree
```

**为什么：**
- 保持主工作树干净，便于并行做其他变更
- 实施走偏时易整体丢弃（`git worktree remove`）
- `tasks.md` 复选框与任何进行中 commit 与其他分支隔离
- 自然配对 `propose.md` §3 的 TDD 每任务一 commit 纪律

**跳过条件（明确判定）：** 满足以下任一即跳过 worktree 创建：
- 单文件改动
- 用户已在 dedicated branch 上工作（用 `git branch --show-current` 检查；分支名非 `main`/`master` 即视为 dedicated）
- 变更预计单次会话内完成

满足跳过条件时不创建 worktree，直接在当前分支实施。

## 完成：先 Converge 再 Archive

当步骤 7 报告"全部完成"（每个任务 `- [x]`），**不要**直接跳到 archive。完成提示增强为两步交接：

1. **第一提示：** "所有任务完成。运行 `/specmark converge` 在归档前把任务与已实施代码对账。"
2. **converge** 关闭任何追加的收敛任务后（重跑 apply 把它们翻为 `- [x]`），**再**提示："运行 `/specmark archive` 归档此变更。"

**为什么 converge 先于 archive：** archive 把变更目录移入 `archive/` 且难以干净撤销。Converge 在漂移还廉价可修时捕获常见失败模式（实施偏离 spec：缺失边界 case、部分覆盖、静默矛盾）。跳过 converge 意味着归档一个代码未完全匹配 spec 的变更 —— 这会损坏 spec 作为未来变更真相来源的地位。

**更新后的完成输出：**

```
## 实施完成

**变更：** <change-name>
**Schema：** <schema-name>
**进度：** N/N 任务完成 ✓

所有任务完成。下一步：
1. `/specmark converge` —— 对账任务 vs 代码（推荐）
2. `/specmark archive` —— 归档此变更（converge 后运行）
```

**Fluid Workflow Integration**

本子命令支持"对变更操作"模型：

- **可随时调用**：产物未全完成前（若任务存在）、部分实施后、与其他操作交错
- **允许产物更新**：若实施暴露设计问题，建议更新产物 —— 非阶段锁定，灵活工作
