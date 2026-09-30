# Archive — 归档已完成的变更

在 specmark 工作流中归档已完成的变更。

**输入**：可选指定变更名和 `--sync` flag。若省略变更名，检查能否从对话上下文推断。若模糊或歧义，**必须**提示用户选择可用变更。`--sync` 启用 delta spec 到主 spec 的同步（默认不同步）。

**Steps**

0. **启动检测：归档目录只读状态**

   归档目录 `specmark/archive/` 是只读历史。`$SKILL/scripts/archive_change.sh` 在创建归档根时会放置 `specmark/archive/.readonly` 哨兵；该脚本对归档目录的**唯一允许写入是追加新条目**，拒绝覆盖/删除既有归档。
   - 若用户请求"修改/删除/重命名既有归档条目"：拒绝，提示新建 change 处理后续变更。
   - 实际归档操作（步骤 4 的可选 sync + 步骤 5 的 mv + 写 meta.json）**必须**通过 `$SKILL/scripts/archive_change.sh` 执行（内含 change 级 fcntl 进程锁、只读强制、commit SHA 锚定），不由 AI 用文件系统工具手动 mv——手动 mv 绕过锁与只读强制，违反确定性逻辑代码化的核心约束。

1. **若未提供变更名，提示选择**

   **🔴 CHECKPOINT · 🛑 STOP：列出活动变更后让用户显式选择，不要自动选；归档是不可逆操作，误归档需手动恢复。**

   用 **Glob 工具**列 `specmark/changes/*/` 目录。用 **AskUserQuestion 工具**让用户选。

   仅显示活动变更（未已归档）。

   **重要**：不要猜测或自动选变更。总让用户选。

2. **检查产物完成状态**

   **必须**调用确定性脚本检查产物完整性（规则 3：确定性逻辑禁止交给模型）：

   ```bash
   bash $SKILL/scripts/check_phase.sh artifacts <name>
   ```

   脚本输出 JSON，含 `proposal`、`design`、`tasks`、`specs`、`spec_count`、`all_present` 字段（缺失时附 `remedy`）。`all_present=1` 表示产物完整。

   这告诉你：
   - `artifacts`：产物文件存在性（`proposal.md` / `design.md` / `tasks.md` 各自存在或缺失）
   - `specs`：delta spec 是否存在（`spec_count` 给出数量）

   **若任一产物文件缺失：**
   - 显示警告列出缺失的产物文件
   - **🔴 CHECKPOINT · 🛑 STOP：用 AskUserQuestion 确认用户是否要带缺失产物继续归档；默认建议先完成，不静默归档。**
   - 用户确认后继续（归档执行时传 `--allow-unfinished`，缺失会记入 meta.json 豁免快照）

3. **检查任务完成状态**

   **必须**调用确定性脚本检查归档就绪状态（规则 3：确定性逻辑禁止交给模型）：

   ```bash
   bash $SKILL/scripts/check_phase.sh archive-readiness <name>
   ```

   脚本输出 JSON：
   - `ready=true` + `total`：所有任务完成，可归档
   - `ready=false` + `remaining`/`total`/`blocked`：仍有未完成任务（阻塞 `[~]` 计入未完成）
   - `ready=false` + `reason="missing artifacts"`：产物文件缺失
   - 任一非 ready 结果都带 `remedy` 字段，按其行动

   也可用 `bash $SKILL/scripts/check_phase.sh tasks <name>` 获取更详细的任务计数（含原始/收敛分类、阻塞清单、收敛轮数）。

   **若发现未完成任务：**
   - 显示警告显示未完成任务数（含阻塞任务）
   - **🔴 CHECKPOINT · 🛑 STOP：带未完成任务归档会让 spec 与代码永久脱钩；用 AskUserQuestion 显式确认，并在归档摘要中记录跳过数量。**
   - 用户确认后继续（归档执行时传 `--allow-unfinished`，快照记入 meta.json 的 `unfinished` 字段；不传时脚本**拒绝归档**退出 1——脚本是硬门禁，AskUserQuestion 只决定是否传豁免 flag）

   **若无任务文件：** 不带任务相关警告继续。

4. **评估 delta spec 同步状态**

   检查 `specmark/changes/<name>/specs/` 处的 delta spec。若无，跳过此步骤。

   **若 delta spec 存在且 `--sync` flag 已传入：**

   合并由确定性脚本 `$SKILL/scripts/merge_delta_spec.py` 完成（**不再启动 LLM 子 agent**——spec 合并是确定性结构操作，按 R-`<cap>`-NNN 键做 ADD/MODIFY/DELETE/KEEP，违反"确定性逻辑禁止交给模型"，故改为显式代码）。语义：

   | 情形   | 条件                          | 行为                       |
   | ------ | ----------------------------- | -------------------------- |
   | ADD    | R-ID 仅在 delta               | 追加（按数字后缀稳定排序） |
   | MODIFY | R-ID 同时在 delta 与 main     | delta 的标题+正文替换 main |
   | DELETE | delta 标题文本为 `~~DELETE~~` | 丢弃该 R-ID                |
   | KEEP   | R-ID 仅在 main                | 原样保留                   |

   `Constraints` / `Out of Scope` 按精确行并集合并（main 在前，delta 独有行追加）。幂等：对同一 (main, delta) 合并两次产生相同字节。
   - 可先 `python3 $SKILL/scripts/merge_delta_spec.py --main specmark/specs/<cap>/spec.md --delta specmark/changes/<name>/specs/<cap>/spec.md --dry-run` 预览合并结果，向用户展示合并摘要。
   - 实际合并由步骤 5 的 `archive_change.sh --sync` 自动对每个 delta spec 调用该脚本，无需手动逐个执行。

   **若 delta spec 存在但未传 `--sync`：** 不同步，直接归档。Delta spec 随变更目录一起归档，保留在 `specmark/archive/YYYY-MM-DD-<name>/specs/` 中作为历史记录。

   **若无 delta spec：** 不带同步提示继续。

5. **执行归档（通过 `$SKILL/scripts/archive_change.sh`）**

   实际的 mv + 只读哨兵维护 + change 级锁 + commit SHA 锚定由确定性执行器完成：

   ```bash
   bash $SKILL/scripts/archive_change.sh <name> [--sync] [--date YYYY-MM-DD] [--allow-unfinished]
   ```

   该脚本（判定与写操作实现在 `$SKILL/scripts/specmark_state.py`，不由 AI 手动 mv）：
   - 获取 change 级独占 **fcntl 进程锁**（`specmark/.locks/<name>.lock`，非阻塞轮询最多等 10s，竞争退出码 2；fcntl 为 POSIX 标准，Linux/WSL/macOS 可用）防并发损坏；
   - **完整性门禁**：存在未完成任务（含 `[~]` 阻塞）或缺失 proposal/design 时**拒绝归档**退出 1（结构化 `error_code` + `remedy`）；仅传 `--allow-unfinished`（须先经用户确认）才放行，并把 `unfinished` 快照写入 meta.json；
   - **只读强制**：创建 `specmark/archive/.readonly` 哨兵（若缺失）；目标 `specmark/archive/<date>-<name>` 已存在时报错退出，拒绝覆盖（锁内二次检查，race-safe）；
   - `--sync` 时对每个 delta spec 调 `$SKILL/scripts/merge_delta_spec.py`（见步骤 4）；合并先全部写入临时文件、全部成功后一次性原子替换——**任何失败不落半程状态**；
   - 原子 `mv specmark/changes/<name> → specmark/archive/<date>-<name>`；
   - 写 `specmark/archive/<date>-<name>/meta.json`：`{"change", "archived_at"(UTC), "commit_sha", "synced", ["unfinished" 豁免快照]}`——把归档锚定到具体 commit；锁文件按设计保留在 `.locks/`（持有期间删除会造成假互斥竞态，少量累积无害），`changes/` 变空时自动清理；
   - 在 `specmark/.specmark-version` 记录首次使用的工作流格式版本（升级兼容判断用）。

   **关于路径：** 归档目录 `specmark/archive/` 与活动目录 `specmark/changes/` 分离 —— 便于 git ignore 活动 `specmark/changes/` 内容同时保留历史归档可追溯。活动 changes 是工作区产物（可丢弃、可重建），归档是长期历史记录（需版本控制保留）。

   **失败处理：** 若脚本退出非 0（锁竞争退出码 2；完整性门禁/输入错误退出码 1；平台无 fcntl 退出码 3），展示 stderr 与 JSON `error_code`/`remedy`，不视为已归档；用户可重试、换 `--date` 或按 `remedy` 行动。

   **误归档恢复：** 用 `bash $SKILL/scripts/archive_change.sh restore <archive-dir-or-name>`（同一把 change 级锁内校验 → 原子移回 `changes/` → 删 meta.json → 按 synced 状态提示主 specs 是否需反向处理）。**禁止手动 mv**——见 `references/troubleshooting.md`。

6. **显示摘要**

   显示归档完成摘要，含：
   - 变更名
   - 归档位置
   - delta spec 是否已同步（若适用）
   - 任何警告备注（未完成产物/任务）

**成功时输出**

```
## 归档完成

**变更：** <change-name>
**归档到：** specmark/archive/YYYY-MM-DD-<name>/
**Commit SHA：** <git HEAD 40-hex 或 "null"（无 git 时）>  ← 锚定到 meta.json
**Delta Specs：** ✓ 已同步到主 specs（或 "无 delta spec" 或 "随变更归档（未同步）"）

所有产物完成。所有任务完成。
```

**Guardrails**

- 未提供时总是提示选变更
- 读 `specmark/changes/<name>/tasks.md` 复选框状态做完成检查
- 不在警告上阻塞归档 —— 仅告知并确认
- 变更目录整体移到归档（含 specs/ 目录，若存在）；无单独配置文件
- 显示清晰的发生了什么摘要
- **归档执行必须走 `$SKILL/scripts/archive_change.sh`** —— 它内含只读哨兵、change 级 fcntl 进程锁、完整性门禁、commit SHA 锚定；不手动 mv
- **归档目录只读** —— `specmark/archive/.readonly` 哨兵存在；既有归档条目禁止修改/删除/重命名，只允许追加新条目
- delta spec 同步仅在传入 `--sync` flag 时执行；默认不同步，delta spec 随变更归档；同步由 `$SKILL/scripts/merge_delta_spec.py` 确定性完成（不启动 LLM 子 agent）
- 归档后 delta spec 保留在 `specmark/archive/YYYY-MM-DD-<name>/specs/` 中，可追溯
