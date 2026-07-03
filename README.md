# Specmark —— 规格驱动变更工作流技能

[![GitHub Release](https://img.shields.io/github/v/release/Kirky-X/specmark?style=flat-square)](https://github.com/Kirky-X/specmark/releases)
[![GitHub License](https://img.shields.io/github/license/Kirky-X/specmark?style=flat-square)](LICENSE)

Specmark 是一个面向 AI agent 的规格驱动变更(spec-driven change)管理 skill，前身是 4 个独立的 `specmark-*` 顶层技能，现已扁平合并为单一 skill。它通过七个子命令构成完整工作流：`explore`（只读探索/思考）→ `clarify`（结构化澄清）→ `propose`（一步生成 proposal + design + tasks 全套产物）→ `analyze`（跨产物一致性检查）→ `apply`（按 tasks.md 逐条实施）→ `converge`（收敛代码与 spec 缺口）→ `archive`（归档已完成变更并评估 delta spec 同步）。

specmark 是**纯文档型 skill**，不依赖任何外部 CLI：所有变更管理操作通过 AI agent 的文件系统工具直接操作 `specmark/` 工作目录完成。各子命令的完整流程、步骤与 Guardrails 见 [SKILL.md](SKILL.md) 与 `references/<子命令>.md`。

## 功能特性

- **七阶段 spec-driven 工作流**：探索 → 澄清 → 提案 → 分析 → 实施 → 收敛 → 归档，非强制线性，可按需跳转
- **自动执行链**：阶段间自动衔接（explore→clarify→propose→analyze→apply→converge→提问），无需手动逐步调用
- **一步生成全套产物**：`propose` 单次产出 `proposal.md` + `design.md` + `tasks.md`
- **长程变更自动生成 delta spec**：任务数 ≥5 或跨 ≥3 模块时，自动在 `specs/<capability>/spec.md` 生成可验证需求规格
- **只读思考模式**：`explore` 不写应用代码，用于梳理想法、对比选项、澄清需求
- **结构化澄清**：`clarify` 跨 8 分类扫描，至多 5 个高影响问题
- **跨产物质量门**：`analyze` 只读检查 proposal/design/tasks/delta-spec 一致性
- **逐条任务追踪**：`apply` 按 `tasks.md` 勾选进度，支持继续中断的 change
- **收敛对账**：`converge` 对比代码与 spec（优先用 delta spec 验收标准），append-only 追加遗漏任务
- **归档时 delta spec 评估**：`archive` 的 `--sync` flag 可将 delta spec 同步到 `specmark/specs/` 主规格
- **Mermaid 流程图**：阶段协作链路、自动执行链、调用示例均以 Mermaid 图表可视化
- **自动链失败模式**：7 种失败条件预定义处理路径（analyze CRITICAL 暂停、converge 循环上限 3 次等）
- **统一入口**：单一 skill 入口，子命令通过 `$ARGUMENTS[0]` 路由

## 安装

### 方式一：通过 `skills` 包安装（推荐）

需 [Node.js](https://nodejs.org/) 18+ 和 `skills` npm 包（v1.5.12+）。`skills` 是 open agent skills 生态的 CLI，支持 68+ agents（Claude Code / Trae / Cursor / Codex / OpenCode 等）。

```bash
# 安装到 Claude Code
npx skills add https://github.com/Kirky-X/specmark.git --agent claude-code -y

# 等价简写(owner/repo)
npx skills add Kirky-X/specmark --agent claude-code -y

# 安装到 Trae
npx skills add Kirky-X/specmark --agent trae -y

# 列出仓库中可被发现的所有 skills(不安装)
npx skills add https://github.com/Kirky-X/specmark.git --list
```

安装后 skill 文件位于对应 agent 的 skills 目录（具体路径由所选 `--agent` 决定，参见各 runtime 文档）。

### 方式二：传统 git clone + install-skill.sh

仓库自带 `scripts/install-skill.sh`，支持 9 种 agent（claude / cursor / windsurf / trae / gemini / copilot / opencode / roocode / qoder）一键安装：

```bash
git clone https://github.com/Kirky-X/specmark.git
cd specmark

# 安装到当前项目的 claude agent 目录
./scripts/install-skill.sh install specmark --agent claude

# 安装到所有支持的 agent
./scripts/install-skill.sh install specmark --all-agents

# 查看支持的 agent 与路径
./scripts/install-skill.sh list-agents
```

脚本会自动把 `SKILL.md` + `skill.json` + `references/` 复制到目标 runtime 的 skills 目录。如需手动安装，请用 `list-agents` 子命令查看各 runtime 对应路径后自行复制。

## 使用示例

Specmark 作为 skill 被 agent 加载后，通过 `$ARGUMENTS[0]` 选择子命令，也支持自然语言意图触发。子命令详细描述与用户意图路由见 [SKILL.md 路由表](./SKILL.md)。

| 子命令     | 一句话功能                                                |
| ---------- | --------------------------------------------------------- |
| `explore`  | 只读探索/思考模式，梳理想法、对比选项、澄清需求           |
| `clarify`  | 结构化澄清，propose 前可选（≤5 高影响问题，8 分类扫描）   |
| `propose`  | 一步生成 proposal + design + tasks 全套产物               |
| `analyze`  | 跨产物一致性分析（只读质量门，propose 后 apply 前）       |
| `apply`    | 按 tasks.md 实施任务，逐条勾选                            |
| `converge` | 收敛：apply 完成后对比代码与 spec，append 缺漏任务        |
| `archive`  | 归档已完成变更，含 delta spec 同步评估                    |

### 调用示例

```text
/specmark propose add-user-auth      # 明确子命令 + 变更名，生成全套产物
/specmark clarify add-user-auth      # propose 前澄清模糊点（≤5 问，8 分类扫描）
/specmark analyze add-user-auth      # 检查 proposal/design/tasks 一致性（只读质量门）
/specmark apply                      # 实施 / 继续当前 change
/specmark converge                   # apply 后对比代码与 spec，append 缺漏任务
/specmark explore                    # 进入只读探索模式
/specmark                            # 无参 → 列出子命令路由表
```

### 自然语言意图触发

```text
「我想做 X / 加个功能」           → propose（生成完整提案）
「需求里有模糊点 / 先问清楚」     → clarify（结构化澄清）
「帮我梳理这个想法 / 探讨方案」   → explore
「提案生成后 / 检查产物一致性」   → analyze（只读质量门）
「开始实施 / 做下一个任务」       → apply
「实施完了 / 对比代码和 spec」    → converge
「这个 change 做完了 / 归档」     → archive
「我还没想好 / 先聊聊」           → explore（用 AskUserQuestion 确认）
```

## 能力概览

### `references/` —— 子命令流程文档

七个子命令的完整 Steps + Guardrails 参考文档：

| 文件                       | 子命令流程                                    |
| -------------------------- | --------------------------------------------- |
| [`explore.md`](references/explore.md)     | explore 子命令流程（只读探索/思考，含深度研究模式）   |
| [`clarify.md`](references/clarify.md)     | clarify 子命令流程（结构化澄清，8 分类扫描）         |
| [`propose.md`](references/propose.md)     | propose 子命令流程（生成全套提案产物 + 模板）        |
| [`analyze.md`](references/analyze.md)     | analyze 子命令流程（只读跨产物一致性检查）           |
| [`apply.md`](references/apply.md)         | apply 子命令流程（按 tasks.md 实施）                 |
| [`converge.md`](references/converge.md)   | converge 子命令流程（收敛代码与 spec 缺口）          |
| [`archive.md`](references/archive.md)     | archive 子命令流程（归档 + delta spec 评估）         |

### `specmark/` —— 变更与规格存储

```
specmark/
├── changes/    # 进行中的变更(proposal/design/tasks)
└── specs/      # 归档后的 delta spec 同步目标
```

### `test-prompts.json` —— 子命令触发测试用例

包含各子命令的触发语测试用例，用于验证 skill 路由正确性。

## 完整流程链路

```
explore（探索）→ clarify（澄清）→ propose（生成提案）→ analyze（一致性分析）→ apply（实施）→ converge（收敛）→ archive（归档）
(只读思考)        (8分类问答)       (proposal/design/tasks) (只读质量门)        (逐条勾选)       (append 缺漏)      (delta spec 同步)
```

1. `explore` 是只读思考模式，可随时进入；想清楚后用 `clarify`（可选）或 `propose` 落地为变更
2. `clarify` 是 propose 前的可选澄清步骤；需求明确时直接跳过
3. `propose` 产出全套产物后，提示运行 `/specmark analyze`（可选质量门）或 `/specmark apply`
4. `analyze` 是 propose 后 apply 前的可选只读质量门；不阻塞 apply
5. `apply` 全部任务完成后，提示先 `/specmark converge` 再 `/specmark archive`
6. `converge` 是 apply 后 archive 前的可选收敛步骤；append-only 追加遗漏任务，再回到 `apply` 关闭
7. 七阶段非强制线性，clarify/analyze/converge 均可按需跳转（见各 references 的 Fluid Workflow Integration）

## 维护说明

本技能原为 4 个独立顶层技能（`specmark-propose` / `specmark-explore` / `specmark-apply-change` / `specmark-archive-change`），现已扁平合并：各原 `SKILL.md` 去除 frontmatter 后成为 `references/{propose,explore,apply,archive}.md`；跨技能交叉引用已改写为本技能子命令（`/specmark apply`、`/specmark propose`）。技能发现机制只识别 `specmark/SKILL.md`，不独立获取 `references/` 内的流程文档。

## FAQ

### `skills` 包版本要求?

需 `skills` npm 包 **v1.5.12+**。`skills` 是 [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) 生态的 CLI，支持 68+ agents。用 `npx skills@latest` 自动获取最新版。

### 远程安装提示"No skills found"?

确认 GitHub 仓库 `Kirky-X/specmark` 已 push 含 `SKILL.md`（根目录，YAML frontmatter 含 `name` + `description`）的最新代码。`skills` 包通过 `git clone` 获取仓库后扫描 `SKILL.md`，仓库为空或缺少 `SKILL.md` 会报该错。

### `skills add` 提示"Installation complete"但 skill 目录不存在?

这是 `skills` 包的已知问题：命令报告成功但未实际复制文件。**Workaround**：用仓库自带的安装脚本重新安装，支持多 runtime：

```bash
# 用 install-skill.sh 重新安装到指定 agent
./scripts/install-skill.sh install specmark --agent claude

# 或查看所有支持的 agent 路径后手动复制
./scripts/install-skill.sh list-agents
```

如需手动复制，`list-agents` 会显示各 runtime 对应的 `folder/subdir` 路径，按需选择后把 `SKILL.md` + `skill.json` + `references/` 复制过去即可。

## 许可证

MIT
