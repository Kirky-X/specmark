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
| 误归档了未完成的变更 | 从 `specmark/archive/<date>-<name>/` 手动 mv 回 `specmark/changes/<name>/` |
| analyze 发现 CRITICAL 问题 | 自动链暂停 → 修复产物 → 重跑 analyze → 继续 apply |
| 自动链误路由（进了错误子命令） | 发出新指令中断链路 → 显式调用正确子命令 |
| delta spec 合并失败 | 检查 `scripts/merge_delta_spec.py` 输出 → 确认 delta spec 格式正确 → 重跑 `--dry-run` |
| 锁竞争失败（archive 退出码 2） | 等待其他进程完成 → 重试，或检查 `specmark/.locks/` 清理残留锁 |

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
# 找到归档位置
ls specmark/archive/*-<change-name>/

# 移回活动目录
mv specmark/archive/<date>-<change-name> specmark/changes/<change-name>

# 删除 meta.json（它是归档标记）
rm specmark/changes/<change-name>/meta.json
```

恢复后运行 `/specmark apply` 继续未完成的任务。

### delta spec 合并失败

**症状：** `archive --sync` 时 `merge_delta_spec.py` 报错。

**常见原因：**

1. delta spec 格式不正确（缺少 `### R-<cap>-NNN:` 标题）
2. capability 名称与目录名不匹配
3. R-ID 格式不符合 `R-<cap>-NNN` 模式

**恢复步骤：**

```bash
# 预览合并（不实际写入）
python3 scripts/merge_delta_spec.py --dry-run \
  --main specmark/specs/<cap>/spec.md \
  --delta specmark/changes/<name>/specs/<cap>/spec.md

# 根据错误输出修正 delta spec 格式
# 然后重新归档
bash scripts/archive_change.sh <name> --sync
```

### 锁竞争失败

**症状：** `archive_change.sh` 退出码 2，报 "无法获取锁"。

**恢复步骤：**

```bash
# 检查谁持有锁
lsof specmark/.locks/<name>.lock 2>/dev/null

# 如果是残留锁（进程已不存在），删除锁文件
rm specmark/.locks/<name>.lock

# 重试归档
bash scripts/archive_change.sh <name> --sync
```

---

## 诊断工具

### 检查变更状态

```bash
# 全局状态概览
bash scripts/status.sh

# 单个变更的产物完整性
bash scripts/check_phase.sh artifacts <name>

# 单个变更的任务完成状态
bash scripts/check_phase.sh tasks <name>

# 是否可进入 converge
bash scripts/check_phase.sh converge-readiness <name>

# 是否可归档
bash scripts/check_phase.sh archive-readiness <name>

# 变更复杂度评估
bash scripts/check_phase.sh complexity <name>
```

### 检查文档一致性

```bash
# 跨文件引用 lint
python3 scripts/check_refs.py --verbose

# JSON 格式输出（CI 集成用）
python3 scripts/check_refs.py --json
```

### 预览归档

```bash
# 预览归档结果（不执行）
bash scripts/archive_change.sh <name> --sync --dry-run
```
