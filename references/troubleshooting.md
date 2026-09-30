# Troubleshooting — 常见问题与恢复

specmark 工作流中常见场景的恢复方法。

---

## 快速恢复表

| 场景 | 恢复方法 |
|------|----------|
| apply 中途发现 design 有误 | 暂停 apply → `/specmark explore` 重新评估 → 更新 design.md → 恢复 apply |
| apply 任务描述不清 | PAUSE 当前任务 → `/specmark propose` 修正 tasks.md → 恢复 apply |
| converge 循环超过 3 次 | 展示 3 轮摘要 → 用户选择接受/手动介入/暂停 |
| 归档后发现 spec 有误 | 新建 change 处理修正（归档只读，不可修改） |
| 误归档了未完成的变更 | `bash $SKILL/scripts/archive_change.sh restore <archive-dir-or-name>`（禁止手动 mv） |
| analyze 发现 CRITICAL 问题 | 自动链暂停 → 修复产物 → 重跑 analyze → 继续 apply |
| 自动链误路由（进了错误子命令） | 发出新指令中断链路 → 显式调用正确子命令 |
| delta spec 合并失败 | 检查 `specmark/scripts/merge_delta_spec.py` 输出 → 确认 delta spec 格式正确 → 重跑 `--dry-run` |
| 锁竞争失败（archive 退出码 2） | 等待其他进程完成 → 重试，或检查 `specmark/.locks/` 清理残留锁 |
| apply 非 code 域阻塞（无可验证交付物） | PAUSE → 检查 proposal.md 的 domain 声明 → 确认任务含 `→ <交付物标识>` → 恢复 apply |
| converge 非 code 域对账失败 | 检查 drift 基线是否匹配 domain → 确认交付物实际存在 → 用对应域的对账策略重跑 |

---

## 详细恢复流程

### apply 中途发现 design 有误

**症状：** 实施过程中发现 design.md 的决策不适用（如选错了技术方案）。

**恢复步骤：**

1. 暂停当前任务（不标记 `- [x]`）
2. 运行 `/specmark explore` 重新评估方案
3. 更新 `design.md` 的 `## Decision` 和 `## Alternatives Considered`
4. 如果影响任务列表，更新 `tasks.md`（可能需要 `/specmark propose` 重新生成）
5. 恢复 `/specmark apply`

**注意：** 不要直接跳过有问题的任务继续后面的——顺序执行是硬约束。

### converge 循环超过 3 次

**症状：** converge→apply→converge 循环 3 次后仍有新缺口。

**恢复步骤：**

1. 系统会强制停止并展示 3 轮摘要
2. 用 AskUserQuestion 选择：
   - **接受当前状态归档** — 如果剩余缺口是装饰性的
   - **手动介入修改 spec** — 如果 spec 本身过于理想化
   - **暂停此变更** — 如果需要时间重新评估
3. 选择后按指示操作

**根因分析：** 通常说明 spec 与实现之间存在根本性分歧，可能需要回到 explore 重新思考。

### 误归档了未完成的变更

**症状：** 不小心归档了还有未完成任务的变更。

**恢复步骤：**

```bash
# 用 restore 子命令恢复（接受完整归档目录名；短名无歧义时也可）
bash $SKILL/scripts/archive_change.sh restore <date>-<change-name>
```

restore 在同一把 change 级锁内完成：校验活动区无同名冲突 → 原子移回 `specmark/changes/<name>/` → 删除 meta.json → 若该归档曾 `--sync`，提示主 specs 仍含其内容（如需回滚主规格须手工编辑 `specmark/specs/`，归档树只读约束不会自动反向合并）。

**常见失败：**

- `active_name_conflict`：活动区已有同名变更 → 先归档或移走它再 restore
- `ambiguous_restore_ref`：短名匹配到多个归档条目 → 改用完整目录名（错误信息会列出候选项）

恢复后运行 `/specmark apply` 继续未完成的任务。**全程不要手动 `mv`**——手动 mv 绕过锁与同名冲突校验，违反 archive.md 的只读强制约束。

### delta spec 合并失败

**症状：** `archive --sync` 时 `merge_delta_spec.py` 报错。

**常见原因：**

1. delta spec 格式不正确（缺少 `### R-<cap>-NNN:` 标题）
2. capability 名称与目录名不匹配
3. R-ID 格式不符合 `R-<cap>-NNN` 模式

**恢复步骤：**

```bash
# 预览合并（不实际写入）
python3 specmark/scripts/merge_delta_spec.py --dry-run \
  --main specmark/specs/<cap>/spec.md \
  --delta specmark/changes/<name>/specs/<cap>/spec.md

# 根据错误输出修正 delta spec 格式
# 然后重新归档
bash specmark/scripts/archive_change.sh <name> --sync
```

### 锁竞争失败

**症状：** `archive_change.sh` 退出码 2，报 "无法获取锁"。

**背景：** 归档锁是 change 级 fcntl 进程锁（`specmark/.locks/<name>.lock`，非阻塞轮询最多等 10s；Linux/WSL/macOS 可用，Windows 原生 Python 无 fcntl 时归档/恢复返回退出码 3）。锁文件在持有期间**不删除**——进程仍持有其锁，删除文件会让新进程锁到新 inode 形成假互斥。

**恢复步骤：**

```bash
# 检查谁持有锁（进程仍在运行则等它完成）
lsof specmark/.locks/<name>.lock 2>/dev/null

# 确认无进程持有后，清理残留锁文件
rm specmark/.locks/<name>.lock

# 重试归档
bash specmark/scripts/archive_change.sh <name> --sync
```

### apply 非 code 域阻塞恢复

**症状：** apply 在非 code 域执行时 PAUSE，报"无可验证交付物"。

**恢复步骤：**

1. 检查 `proposal.md` 头部是否有 `<!-- domain: <type> -->` 声明
   - 无声明 → 默认 `code` 域，可能误判。添加正确的 domain 声明
2. 检查 `tasks.md` 中阻塞任务是否含 `→ <交付物标识>`
   - 缺失 → 用 `/specmark propose` 修正 tasks.md，补充交付物标识
3. 确认 domain 与任务格式匹配（见 propose.md 各域交付物标识表）
4. 恢复 `/specmark apply`

**常见错误：**
- `doc` 域任务未写 `→ docs/xxx.md` → 被当作 code 域处理，找不到源码文件
- `event` 域任务未写行动标识 → apply 无法判定交付物

### 非 code 域 converge 对账

**症状：** converge 在非 code 域执行时无法对账，或 drift 基线不适用。

**恢复步骤：**

1. 确认 proposal.md 的 domain 声明正确
2. 检查 converge 使用的 drift 基线是否匹配 domain：
   - `code` → git diff
   - `doc` → 内容 diff（对比交付文档与 delta spec）
   - `event` → 行动记录对比
   - `design` → 设计稿对比
   - `research` → 报告对比
   - `general` → 交付物描述对比
3. 若基线不匹配，检查 converge.md 步骤 2 的 domain 分派表是否已更新
4. 非 code 域的 converge 对账以交付物标识定位实际产出，而非源码路径

---

## 诊断工具

### 检查变更状态

```bash
# 全局状态概览
bash $SKILL/scripts/status.sh

# 单个变更的产物完整性
bash specmark/scripts/check_phase.sh artifacts <name>

# 单个变更的任务完成状态
bash specmark/scripts/check_phase.sh tasks <name>

# 是否可进入 converge
bash specmark/scripts/check_phase.sh converge-readiness <name>

# 是否可归档
bash specmark/scripts/check_phase.sh archive-readiness <name>

# 变更复杂度评估
bash specmark/scripts/check_phase.sh complexity <name>
```

### 检查文档一致性

```bash
# 用户项目：活动变更产物 lint（占位符 / 任务 ID / 优先级 / 路径存在性）
python3 $SKILL/scripts/check_refs.py --project <project-root>

# specmark skill 仓库：references 跨文件引用 lint
python3 $SKILL/scripts/check_refs.py --skill-root <skill-repo> --verbose

# JSON 格式输出（CI 集成用）
python3 $SKILL/scripts/check_refs.py --project <project-root> --json
```

### 预览归档

```bash
# 预览归档结果（不执行）
bash specmark/scripts/archive_change.sh <name> --sync --dry-run
```
