# Status — 全局状态查询

查看 specmark 工作目录的活动变更与历史归档概览。

**定位**：只读查询，不修改任何产物或状态。随时可调用。

**输入**：无必需参数。`/specmark status` 即可。

---

## Steps

1. **运行状态查询脚本**

   调用 `scripts/status.sh` 获取全局状态：

   ```bash
   bash scripts/status.sh          # 人类可读表格
   bash scripts/status.sh --json   # JSON 格式（程序化处理）
   ```

   脚本自动扫描 `specmark/changes/` 和 `specmark/archive/` 目录。

2. **展示活动变更**

   对每个活动变更显示：

   | 字段 | 来源 |
   |------|------|
   | 变更名 | `specmark/changes/*/` 目录名 |
   | 当前阶段 | 推断自产物存在性 + tasks.md 完成状态 |
   | 任务进度 | `tasks.md` 中 `- [x]` / `- [ ]` 计数 |
   | delta spec | `specs/` 下 `spec.md` 文件数 |

   **阶段推断规则**（由 `scripts/check_phase.sh` 确定性执行）：

   | 条件 | 推断阶段 |
   |------|----------|
   | 无产物文件 | `new` |
   | 有 proposal.md 无 tasks.md | `propose` |
   | 有 tasks.md 且有未完成原始任务 | `apply` |
   | 所有原始任务 `- [x]`，有/无收敛任务 | `converge` |

3. **展示已归档变更（最近 5 个）**

   对每个归档条目显示：

   | 字段 | 来源 |
   |------|------|
   | 归档目录名 | `specmark/archive/*/` 目录名 |
   | 归档日期 | `meta.json` → `archived_at` |
   | synced | `meta.json` → `synced`（✓/✗） |
   | commit SHA | `meta.json` → `commit_sha`（前 7 位） |

4. **提供下一步建议**

   根据活动变更状态给出建议：

   | 状态 | 建议 |
   |------|------|
   | 无活动变更 | "运行 `/specmark explore` 探索想法，或 `/specmark propose <name>` 开始新变更" |
   | 有 `apply` 阶段变更 | "运行 `/specmark apply` 继续实施" |
   | 有 `converge` 阶段变更 | "运行 `/specmark converge` 对账，或 `/specmark archive` 归档" |

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
