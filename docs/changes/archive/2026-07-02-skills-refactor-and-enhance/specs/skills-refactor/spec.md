# Spec — Skills Refactor and Enhance

## Requirements

### REQ-001: Skill 重命名
- openspec 目录改名为 specmark
- methodology 目录改名为 kueiku
- review 目录改名为 diting
- security-audit 目录改名为 tiangang
- pangu 目录保持不变
- 4 个 SKILL.md 的 frontmatter name 字段更新为新名称
- specmark SKILL.md 中 11 处命令路径引用从 /openspec 改为 /specmark
- specmark 的 reference/ 目录改名为 references/
- 外部 openspec CLI 引用（openspec new/status/instructions/list）保持不变

### REQ-002: 模板结构对齐
- 5 个 skill（specmark/kueiku/diting/tiangang/pangu）各自补齐以下文件：
  - .gitignore（优化版，含 OS/IDE/Python/Node/env/log/Meta 忽略项）
  - LICENSE（MIT，copyright 2026）
  - README.md（中文，含 badge/安装/使用/能力概览）
  - README_EN.md（英文镜像）
  - skill.json（8 字段：name/displayName/version/description/license/keywords/homepage/repository）
  - .claude-plugin/marketplace.json（极简模板）
  - .github/workflows/release.yml（tag v* 触发 GitHub Release）
  - .claude/skills/gitnexus/（6 个子 skill，从 maliang 复制）
  - openspec/（含 changes/ + specs/ 空目录）
  - test-prompts.json（缺失的补齐）
- 5 个 SKILL.md frontmatter 加 license: MIT 字段
- maliang/.gitignore 优化（添加常见忽略项）

### REQ-003: 独立 git 仓库
- 5 个 skill 各自在目录内执行 git init
- 首次 commit 包含所有最终文件
- 不自动 push 到远程

### REQ-004: Specmark 能力增强
- 新增 references/clarify.md（结构化澄清子命令）
- 新增 references/analyze.md（跨产物一致性分析子命令）
- 新增 references/converge.md（收敛子命令）
- SKILL.md 路由表新增 clarify/analyze/converge 三个子命令
- references/propose.md 增强：Task 格式 5 元素 / Self-Review / No Placeholders / NEEDS CLARIFICATION / Bite-sized TDD
- references/apply.md 增强：前置 critical review / finishing 步骤

### REQ-005: Kueiku 能力增强
- 新增约 37 个方法论 reference 文件（7 个新类别）
- SKILL.md 路由表新增 7 个类别
- 增强 4 个现有方法论文件（north-star / value-proposition-canvas / rice / premortem-counterfactual）

### REQ-006: Diting 能力增强
- 新增 references/commands/agent.md（review agent 子维度）
- 含 7 个可检测审核方法（F01/F02/F03/F05/F07/F08/F09）
- SKILL.md 更新 Engine A 维度列表新增 agent

### REQ-007: Maliang 能力增强
- 新增 references/meta/ 下 7 个文件
- 新增 references/commands/redesign.md
- 新增 references/dimensions/ 下 2 个文件
- 新增 references/framework/motion-skeletons/ 目录
- 新增 references/vocabulary/ 目录
- 增强 principles.md / color.md / token.md / design-md.md / preview.md

### REQ-008: Tiangang 能力增强
- 新增 references/agent-semgrep-rules.md
- 补齐 test-prompts.json

### REQ-009: Pangu 能力增强
- 新增 scripts/init-skill.sh
- 新增 scripts/align-skill.sh
- 新增 templates/skill/ 模板目录

### REQ-010: 共享脚本套件
- 项目根新增 script/ 目录
- 新增 script/install-skill.sh（安装 skill 到项目级 agent）
- 6 个 skill 的 script/ 软链接到项目根 script/

### REQ-011: 命名规范验证
- 所有文件夹名全小写
- 所有 README 标题首字母大写
- 所有 skill.json name 字段全小写
- 所有 SKILL.md frontmatter name 全小写

### REQ-012: .gitignore 优化
- maliang/.gitignore 优化
- 5 个新 skill 的 .gitignore 使用优化版
- 添加 .DS_Store / .meta / .vscode / __pycache__ / *.pyc / node_modules / .idea / *.log / .env 等
