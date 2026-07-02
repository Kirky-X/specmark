# Archive — 归档已完成的变更

在 specmark 工作流中归档已完成的变更。

**输入**：可选指定变更名。若省略，检查能否从对话上下文推断。若模糊或歧义，**必须**提示用户选择可用变更。

**Steps**

1. **若未提供变更名，提示选择**

   **🔴 CHECKPOINT · 🛑 STOP：列出活动变更后让用户显式选择，不要自动选；归档是不可逆操作，误归档需手动恢复。**

   用 **Glob 工具**列 `specmark/changes/*/` 目录。用 **AskUserQuestion 工具**让用户选。

   仅显示活动变更（未已归档）。
   若可用，显示每个变更所用 schema。

   **重要**：不要猜测或自动选变更。总让用户选。

2. **检查产物完成状态**

   读 `specmark/changes/<name>/tasks.md` 复选框状态（`- [ ]` 未完成 / `- [x]` 完成）检查产物完成度。

   这告诉你：
   - `schemaName`：使用的工作流
   - `artifacts`：产物列表及其状态（`done` 或其他）

   **若任一产物非 `done`：**
   - 显示警告列出未完成产物
   - **🔴 CHECKPOINT · 🛑 STOP：用 AskUserQuestion 确认用户是否要带未完成产物继续归档；默认建议先完成，不静默归档。**
   - 用 **AskUserQuestion 工具**确认用户想继续
   - 用户确认后继续

3. **检查任务完成状态**

   读任务文件（通常 `tasks.md`）检查未完成任务。

   计数 `- [ ]`（未完成）vs `- [x]`（完成）任务。

   **若发现未完成任务：**
   - 显示警告显示未完成任务数
   - **🔴 CHECKPOINT · 🛑 STOP：带未完成任务归档会让 spec 与代码永久脱钩；用 AskUserQuestion 显式确认，并在归档摘要中记录跳过数量。**
   - 用 **AskUserQuestion 工具**确认用户想继续
   - 用户确认后继续

   **若无任务文件：** 不带任务相关警告继续。

4. **评估 delta spec 同步状态**

   检查 `specmark/changes/<name>/specs/` 处的 delta spec。若无，不带同步提示继续。

   **若 delta spec 存在：**
   - 把每个 delta spec 与 `specmark/specs/<capability>/spec.md` 处对应主 spec 对比
   - 确定会应用什么变更（增、改、删、重命名）
   - 提示前显示合并摘要

   **提示选项：**
   - 若需变更："立即同步（推荐）"、"不同步直接归档"
   - 若已同步："立即归档"、"仍同步"、"取消"

   若用户选同步，启动子 agent 同步 delta spec 到 `specmark/specs/<capability>/spec.md`（用当前 runtime 的子 agent 机制，把已分析的 delta —— 增、改、删、重命名 —— 应用到对应主 spec 文件；agent 驱动）。把已分析的 delta spec 摘要传入 prompt。不论选什么都继续归档。

5. **执行归档**

   若归档目录不存在则创建：

   ```bash
   mkdir -p docs/changes/archive
   ```

   **关于路径：** 归档目录 `docs/changes/archive/` 与活动目录 `specmark/changes/` 分离 —— 便于 git ignore 活动 `specmark/changes/` 内容同时保留历史归档可追溯。活动 changes 是工作区产物（可丢弃、可重建），归档是长期历史记录（需版本控制保留）。

   用当前日期生成目标名：`YYYY-MM-DD-<change-name>`

   **检查目标是否已存在：**
   - 是：报错失败，建议重命名已有归档或用不同日期
   - 否：把变更目录移到归档

   ```bash
   mv specmark/changes/<name> docs/changes/archive/YYYY-MM-DD-<name>
   ```

6. **显示摘要**

   显示归档完成摘要，含：
   - 变更名
   - 使用 schema
   - 归档位置
   - spec 是否已同步（若适用）
   - 任何警告备注（未完成产物/任务）

**成功时输出**

```
## 归档完成

**变更：** <change-name>
**Schema：** <schema-name>
**归档到：** docs/changes/archive/YYYY-MM-DD-<name>/
**Specs：** ✓ 已同步到主 specs（或 "无 delta spec" 或 "同步已跳过"）

所有产物完成。所有任务完成。
```

**Guardrails**

- 未提供时总是提示选变更
- 读 `specmark/changes/<name>/tasks.md` 复选框状态做完成检查
- 不在警告上阻塞归档 —— 仅告知并确认
- 变更目录整体移到归档；无单独配置文件
- 显示清晰的发生了什么摘要
- 若请求同步，agent 侧驱动：把 delta spec 变更应用到主 specs
- 若 delta spec 存在，总是跑同步评估并在提示前显示合并摘要
