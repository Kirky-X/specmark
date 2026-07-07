# Converge — 归档前把任务与已实施代码对账

`apply`（所有任务标记 `- [x]`）与 `archive` 之间的可选步骤。Converge 把实际代码与变更产物对比（若存在 delta spec 则优先对比 spec），找出实施偏离或未覆盖需求的缺口，并**追加**缺失任务到 `tasks.md` 的新 `## Phase N: Convergence` 节。仅追加：converge 绝不重写或删除已有任务。

**定位**：在 `apply` 报告所有任务完成后、`archive` 之前。变更非平凡且实施可能已偏离 spec 时使用（如范围蔓延、跳过边界 case、实施中所做决策未回传）。

**输入**：可选指定变更名。若省略，从上下文推断或用 Glob 工具列 `specmark/changes/*/` 目录（子目录名即变更名）。要求 `tasks.md` 所有原始任务标记 `- [x]`（否则：建议先完成 `apply`）。

**Steps**

1. **验证 apply 已完成**

   读 `tasks.md`。若任何任务在现有 `## Phase N: Convergence` 节外是 `- [ ]`，暂停并建议："Apply 未完成（N 个任务开放）。先完成 `/specmark apply` 再 converge。"不继续。

2. **读取产物与已实施代码（用 `git diff` 做 drift 基线）**

   完整读 `proposal.md`、`design.md`、`tasks.md`。检查 `specmark/changes/<name>/specs/` 是否存在 delta spec 文件——若存在，优先读取 delta spec 作为对比的规格依据（delta spec 定义了该能力域的可验证需求）。然后定位并读任务触及的代码（任务描述中的文件路径 + 标准源码根）。对比是代码对 spec（有 delta spec 时）或代码对 proposal/design（无 delta spec 时），不是 spec 对 spec。

   **drift 基线（git 集成）**：若仓库是 git，用 `git diff` 确定本变更实际改动的代码范围，作为缺口扫描的事实基线，避免遗漏未声明改动或误把无关文件纳入对比：

   ```bash
   # 优先基线：归档锚定的 commit（若 change 的 meta.json 存在 commit_sha）；否则用变更开始前的 commit
   BASE="<change meta.json 的 commit_sha 或 main 分支>"
   git diff --name-only "$BASE"...HEAD -- <任务描述涉及的源码根>
   ```

   - 用 diff 输出的文件清单（而非仅 `tasks.md` 列出的路径）作为代码侧扫描范围——apply 实施中可能产生任务描述未列的连带改动，`git diff` 能暴露这些 drift。
   - 非 git 仓库：回退到任务描述中的文件路径 + 标准源码根，并在收敛叙述中标注"未用 git diff 基线"。
   - diff 基线只用于**圈定扫描范围**；缺口的判定仍由步骤 3 的 4-pass 对比（代码行为 vs spec 需求）决定。

3. **跑 4 个缺口类型 pass**

   每个 pass，把代码行为与 spec 陈述的需求/设计对比并记录缺口。

   | 缺口类型    | 含义                                                   |
   | ----------- | ------------------------------------------------------ |
   | missing     | Spec 要求 X；代码无 X 的实现                           |
   | partial     | Spec 要求 X；代码实现了 X 的一部分（缺子 case 或分支） |
   | contradicts | Spec 说 X；代码做 Y（真正矛盾，非仅不完整）            |
   | unrequested | 代码做 Z；spec 从未要 Z（范围蔓延 / 投机功能）         |

4. **为每个缺口分配严重度**

   | 严重度   | 含义                                      |
   | -------- | ----------------------------------------- |
   | CRITICAL | 与核心需求矛盾，或缺失安全/数据完整性需求 |
   | HIGH     | 主功能需求缺失/部分                       |
   | MEDIUM   | 边界 case 或 NFR 缺失/部分                |
   | LOW      | 未请求的次要便利；装饰性漂移              |

5. **对 CRITICAL/HIGH/MEDIUM 缺口，追加收敛任务**

   **🔴 CHECKPOINT · 🛑 STOP：追加前先确认每个待追加任务确实对应 CRITICAL/HIGH/MEDIUM 缺口且非装饰性 —— 拒绝"顺便优化""锦上添花"类任务污染 tasks.md。逐条念出任务描述 + 缺口类型 + 严重度，自检"这个任务不写，spec 与代码会真正矛盾或缺失吗？"答"否"则降级为 LOW/unrequested，仅记录到收敛叙述。**

   向 `tasks.md` 追加新节：

   ```markdown
   ## Phase N: Convergence

   _由 /specmark converge 于 YYYY-MM-DD 生成。仅追加：不要编辑之前的任务。_

   - [ ] [T###] [P1] [Story?] <缺口描述> — file: <path>
   - [ ] [T###] [P2] [Story?] <缺口描述> — file: <path>
   ```

   - 用**下一个可用 T### ID**（不重排已有任务）。
   - 每个新任务遵循 propose.md 5 元素格式：`- [ ] [T###] [P?] [Story?] Description with file path`。
   - 跳过 LOW 且 `unrequested` 的缺口 —— 记录到收敛叙述（见步骤 6）但不创建任务；用户可接受范围蔓延或另起 follow-up 变更。
   - `contradicts` 缺口总是产出任务，不论严重度（矛盾必须解决，不静默接受）。

6. **在任务列表上方写收敛叙述**

   在 `## Phase N: Convergence` 节的新 `- [ ]` 行上方，记录简短叙述以便 archive 后讲清故事：

   ```markdown
   ## Phase N: Convergence

   _由 /specmark converge 于 YYYY-MM-DD 生成。_

   **发现缺口：** N (CRITICAL: a | HIGH: b | MEDIUM: c | LOW: d)
   **追加任务：** M（跳过：K 个 LOW/unrequested，记录为叙述）
   **未请求范围（按原样接受）：** <项目列表，或 "无">

   - [ ] [T###] ...
   ```

7. **自动回到 apply 关闭追加任务**

   若追加了收敛任务，自动回到 `apply` 关闭它们（无需用户手动调用）。apply 关闭后再次 converge 检查，直到无新缺口。

   **硬规则：循环上限 3 次。** converge→apply→converge 循环超过 3 次仍有新缺口时，**强制停止**：
   - 展示 3 轮收敛摘要（每轮追加了什么、为什么）
   - 用 **AskUserQuestion 工具**问用户：接受当前状态归档 / 手动介入修改 spec / 暂停此变更
   - 不自动第 4 次 converge

**输出**

```
## 收敛完成

**变更：** <name>
**发现缺口：** N (CRITICAL: a | HIGH: b | MEDIUM: c | LOW: d)
**追加任务：** M → tasks.md `## Phase N: Convergence`
**未请求范围已接受：** <count>（见叙述）

自动回到 apply 关闭追加任务…
```

**Guardrails**

- **仅追加** —— 绝不重写、重排或删除已有任务。收敛任务在自己的 `## Phase N: Convergence` 标题下，用下一个可用 ID。
- **所有原始任务必须 `- [x]`** —— converge 不救援半完成的 apply。若任务仍开放，重定向到 `apply`。
- **对比代码，不只对比产物** —— 只读 spec 推断缺口会破坏目的。实施才是实际做了什么的真相来源。
- **有 delta spec 时优先用 spec 对比** —— delta spec 定义了精确的验收标准，比 proposal/design 的描述更直接可检查。
- **`contradicts` 总产出任务** —— 即使 LOW 严重度矛盾也产出任务；静默接受矛盾会损坏 spec。
- **`unrequested` LOW 不产出任务** —— 仅记录到叙述。强制清理每个次要范围蔓延会让变更臃肿。
- **不编辑 proposal.md 或 design.md** —— converge 把任务对账到代码；若 spec 本身错了，那是单独的 propose/explore 决策，不是 converge 行动。
- **可重跑** —— 若 apply 关闭 Phase N 任务后出现新漂移，converge 可追加 `## Phase N+1: Convergence`。每次运行是新 phase。

**Fluid Workflow Integration**

- 处于 `apply`（完成）与 `archive` 之间。自动链中由 apply 完成后自动触发。
- 与 `analyze` 配对：analyze 找 apply 前的 spec↔tasks 漂移；converge 找 apply 后的 tasks↔code 漂移。两者一起覆盖双向。
- converge 追加任务后，自动回到 `apply` 关闭它们（循环上限 3 次）；`archive` 仅在所有 phase（含收敛 phase）都 `- [x]` 时运行。
