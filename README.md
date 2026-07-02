# Specmark —— 规格驱动变更工作流技能

[![GitHub Release](https://img.shields.io/github/v/release/Kirky-X/specmark?style=flat-square)](https://github.com/Kirky-X/specmark/releases)
[![GitHub License](https://img.shields.io/github/license/Kirky-X/specmark?style=flat-square)](LICENSE)

Specmark 是一个面向 AI agent 的规格驱动变更(spec-driven change)管理 skill，前身是 4 个独立的 `specmark-*` 顶层技能，现已扁平合并为单一 skill。它通过四个子命令构成完整工作流：`explore`（只读探索/澄清）→ `propose`（一步生成 proposal + design + tasks 全套产物）→ `apply`（按 tasks.md 逐条实施）→ `archive`（归档已完成变更并评估 delta spec 同步）。

specmark 是**纯文档型 skill**，不依赖任何外部 CLI：所有变更管理操作通过 AI agent 的文件系统工具直接操作 `specmark/` 工作目录完成。各子命令的完整流程、步骤与 Guardrails 见 [SKILL.md](SKILL.md) 与 `references/<子命令>.md`。

## 功能特性

- **四阶段 spec-driven 工作流**：探索 → 提案 → 实施 → 归档，非强制线性，可按需跳转
- **一步生成全套产物**：`propose` 单次产出 `proposal.md` + `design.md` + `tasks.md`
- **只读思考模式**：`explore` 不写应用代码，用于梳理想法、对比选项、澄清需求
- **逐条任务追踪**：`apply` 按 `tasks.md` 勾选进度，支持继续中断的 change
- **归档时 delta spec 评估**：`archive` 自动评估是否需要同步 delta spec 到 `specmark/specs/`
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

安装后 skill 文件位于对应 agent 的 skills 目录（如 `.claude/skills/specmark/`）。

### 方式二：传统 git clone

```bash
git clone https://github.com/Kirky-X/specmark.git
# 将 SKILL.md + references/ 链接或复制到 agent skills 目录
# 各 runtime 的 skills 目录路径示例(任选其一):
#   Claude Code:  ~/.claude/skills/specmark/
#   Trae:         ~/.trae-cn/skills/specmark/
#   Cursor:       ~/.cursor/skills/specmark/
#   Codex:        ~/.codex/skills/specmark/
```

### 无外部依赖

Specmark 是纯文档型 skill，不需要安装任何外部 CLI。所有变更管理操作通过 AI agent 的文件系统工具直接完成。

## 使用示例

Specmark 作为 skill 被 agent 加载后，通过 `$ARGUMENTS[0]` 选择子命令，也支持自然语言意图触发。子命令详细描述与用户意图路由见 [SKILL.md 路由表](./SKILL.md)。

| 子命令   | 一句话功能                                                |
| -------- | --------------------------------------------------------- |
| `explore`  | 只读探索/思考模式，梳理想法、对比选项、澄清需求           |
| `propose`  | 一步生成 proposal + design + tasks 全套产物               |
| `apply`    | 按 tasks.md 实施任务，逐条勾选                            |
| `archive`  | 归档已完成变更，含 delta spec 同步评估                    |

### 调用示例

```text
/specmark propose add-user-auth      # 明确子命令 + 变更名，生成全套产物
/specmark apply                      # 实施 / 继续当前 change
/specmark archive                    # 归档已完成的 change
/specmark explore                    # 进入只读探索模式
/specmark                            # 无参 → 列出子命令路由表
```

### 自然语言意图触发

```text
「我想做 X / 加个功能」           → propose（生成完整提案）
「帮我梳理这个想法 / 探讨方案」   → explore
「开始实施 / 做下一个任务」       → apply
「这个 change 做完了 / 归档」     → archive
「我还没想好 / 先聊聊」           → explore（用 AskUserQuestion 确认）
```

## 能力概览

### `references/` —— 子命令流程文档

四个子命令的完整 Steps + Guardrails 参考文档：

| 文件                       | 子命令流程                                  |
| -------------------------- | ------------------------------------------- |
| [`explore.md`](references/explore.md)   | explore 子命令流程（只读探索/澄清）         |
| [`propose.md`](references/propose.md)   | propose 子命令流程（生成全套提案产物）      |
| [`apply.md`](references/apply.md)       | apply 子命令流程（按 tasks.md 实施）        |
| [`archive.md`](references/archive.md)   | archive 子命令流程（归档 + delta spec 评估）|

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
explore（探索/澄清）→ propose（生成提案）→ apply（实施）→ archive（归档）
(只读思考)            (proposal/design/tasks) (逐条勾选)     (delta spec 同步)
```

1. `explore` 是只读思考模式，可随时进入；想清楚后用 `propose` 落地为变更
2. `propose` 产出全套产物后，提示运行 `/specmark apply`
3. `apply` 全部任务完成后，提示归档（`/specmark archive`）
4. `archive` 评估 delta spec 是否需要同步到 `specmark/specs/`
5. 四阶段非强制线性，可按需跳转（见各 references 的 Fluid Workflow Integration）

## 维护说明

本技能原为 4 个独立顶层技能（`specmark-propose` / `specmark-explore` / `specmark-apply-change` / `specmark-archive-change`），现已扁平合并：各原 `SKILL.md` 去除 frontmatter 后成为 `references/{propose,explore,apply,archive}.md`；跨技能交叉引用（如 `/opsx:apply`、`specmark-continue-change`）已改写为本技能子命令（`/specmark apply`、`/specmark propose`）。技能发现机制只识别 `specmark/SKILL.md`，不独立获取 `references/` 内的流程文档。

## FAQ

### `skills` 包版本要求?

需 `skills` npm 包 **v1.5.12+**。`skills` 是 [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) 生态的 CLI，支持 68+ agents。用 `npx skills@latest` 自动获取最新版。

### 远程安装提示"No skills found"?

确认 GitHub 仓库 `Kirky-X/specmark` 已 push 含 `SKILL.md`（根目录，YAML frontmatter 含 `name` + `description`）的最新代码。`skills` 包通过 `git clone` 获取仓库后扫描 `SKILL.md`，仓库为空或缺少 `SKILL.md` 会报该错。

### `skills add` 提示"Installation complete"但 `.claude/skills/specmark/` 不存在?

这是 `skills` 包的已知问题：命令报告成功但未实际复制文件。**Workaround**：手动复制 skill 文件到 agent skills 目录（以下为各 runtime 路径示例，Claude Code / Trae / Cursor / Codex 任选其一）：

```bash
# Claude Code
mkdir -p ~/.claude/skills/specmark
cp -r SKILL.md skill.json references ~/.claude/skills/specmark/

# Trae
mkdir -p ~/.trae-cn/skills/specmark
cp -r SKILL.md skill.json references ~/.trae-cn/skills/specmark/

# Cursor
mkdir -p ~/.cursor/skills/specmark
cp -r SKILL.md skill.json references ~/.cursor/skills/specmark/

# Codex
mkdir -p ~/.codex/skills/specmark
cp -r SKILL.md skill.json references ~/.codex/skills/specmark/
```

## 许可证

MIT
