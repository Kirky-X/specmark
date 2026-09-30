# Status — 全局状态查询

查看 specmark 工作目录的活动变更与历史归档概览。

**定位**：只读查询，不修改任何产物或状态。随时可调用。

**输入**：无必需参数。`/specmark status` 即可。

---

## Steps

1. **运行状态查询脚本**

   调用 `$SKILL/scripts/status.sh` 获取全局状态：

   ```bash
   bash $SKILL/scripts/status.sh          # 人类可读表格（含「建议下一步」）
   bash $SKILL/scripts/status.sh --json   # JSON 格式（程序化处理，含 next_command）
   ```

   脚本自动扫描 `specmark/changes/` 和 `specmark/archive/` 目录。阶段推断、任务计数、归档解析统一由 `$SKILL/scripts/specmark_state.py`（单一谓词源，与 check_phase.sh 共用同一实现）完成。

2. **展示活动变更**

   对每个活动变更显示：

   | 字段 | 来源 |
   |------|------|
   | 变更名 | `specmark/changes/*/` 目录名 |
   | 当前阶段 | 推断自产物存在性 + tasks.md 完成状态（见下方规则表） |
   | 任务进度 | `tasks.md` 中 `- [x]` / `- [ ]` 计数（completed/total） |
   | 阻塞 | `- [~]` 任务数 |
   | delta spec | `specs/` 下 `spec.md` 文件数 |

   **阶段推断规则**（由 `$SKILL/scripts/specmark_state.py` 确定性执行，`check_phase.sh` 与 `status.sh` 共用）：

   | 条件 | 推断阶段 |
   |------|----------|
   | 无 proposal/design/tasks（specs/ 不参与阶段判定） | `new` |
   | 无 proposal.md，仅 design.md | `explore` |
   | 有 proposal.md 且无 tasks.md（或 tasks.md 内 0 任务） | `propose` |
   | 有 tasks.md 且原始任务未全勾 | `apply` |
   | 原始任务全部 `- [x]`（收敛任务可有未完成） | `converge` |

3. **展示已归档变更（最近 5 个）**

   对每个归档条目显示：

   | 字段 | 来源 |
   |------|------|
   | 归档目录名 | `specmark/archive/*/` 目录名 |
   | 归档日期 | `meta.json` → `archived_at` |
   | synced | `meta.json` → `synced`（✓/✗） |
   | commit SHA | `meta.json` → `commit_sha`（前 7 位） |

4. **提供下一步建议（脚本确定性路由）**

   `--json` 输出的 `next_command` 字段给出全局建议（按 converge > apply > propose > new 优先级，由脚本从阶段推断结果确定性推导）；人类可读表格末行「建议下一步」显示同一结论。直接展示，不再自行推导：

   | 状态 | 脚本 next_command |
   |------|------|
   | 无活动变更 | `/specmark explore 或 /specmark propose <name>` |
   | 有 `converge` 阶段变更 | `/specmark converge <name>` |
   | 有 `apply` 阶段变更 | `/specmark apply <name>` |
   | 仅 `propose`/`new` 阶段变更 | `/specmark propose <name>` |

---

## 输出

```
## Specmark 状态

**活动变更：** 2 个

| 变更名 | 阶段 | 进度 | delta spec |
|--------|------|------|------------|
| add-auth | apply | 3/7 | 2 个 |
| fix-bugs | converge | 6/6 | 1 个 |

**已归档变更：** 无
```

**Guardrails**

- **只读** —— status 绝不修改任何产物、任务状态或归档。
- **不阻塞** —— status 可随时调用，不在自动链中。
- **确定性** —— 所有状态由脚本计算，不依赖 agent 主观判断。

**Fluid Workflow Integration**

- 可在任何阶段调用，不影响自动链。
- 适合在会话开始时快速了解当前工作目录状态。
- 与 `check_phase.sh` 配合：status 给全局视图，check_phase 给单个变更的详细判定。
