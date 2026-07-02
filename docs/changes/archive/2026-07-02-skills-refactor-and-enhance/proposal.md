## Why

当前 6 个 skill（openspec/methodology/review/security-audit/pangu/maliang）发展不均衡：maliang 已有完整的 git 仓库+模板结构（LICENSE/README/skill.json/.github/.claude-plugin 等），其余 5 个 skill 缺少这些基础设施，无法独立分发。同时，通过分析 temp/ 下 8 个参考项目，发现各 skill 在方法论覆盖、审核维度、设计原则上存在显著缺口。本次变更统一 6 个 skill 的仓库结构、重命名 4 个 skill、并基于分析结果扩展各 skill 的能力。

## What Changes

### 重命名与仓库初始化（**BREAKING**）
- openspec → specmark（文件夹 specmark，文档名 Specmark）
- methodology → kueiku（文件夹 kueiku，文档名 Kueiku）
- review → diting（文件夹 diting，文档名 Diting）
- security-audit → tiangang（文件夹 tiangang，文档名 Tiangang）
- pangu 保持不变
- 5 个 skill（specmark/kueiku/diting/tiangang/pangu）各自初始化独立 git 仓库
- 5 个 skill 对齐 maliang 模板结构：补齐 .gitignore / LICENSE / README.md / README_EN.md / skill.json / .claude-plugin/marketplace.json / .github/workflows/release.yml / .claude/skills/gitnexus/ / openspec/ / test-prompts.json（缺失的）
- openspec 的 reference/（单数）改名为 references/（复数），同步更新 SKILL.md 内 5 处路径引用
- 5 个 SKILL.md frontmatter 加 license: MIT 字段

### Specmark 能力增强（吸收 spec-kit/writing-plans/executing-plans）
- 新增 clarify 子命令（结构化澄清，最多 5 问，8 分类覆盖扫描）
- 新增 analyze 子命令（只读跨产物一致性分析，6 种检测+4 级严重度）
- 新增 converge 子命令（实施后代码-spec 差距检查，append-only 收敛）
- propose 增强：Task 格式 5 元素规范 / Self-Review 三项检查 / No Placeholders 硬规则 / NEEDS CLARIFICATION 机制 / Bite-sized TDD 颗粒度
- apply 增强：前置 critical review / git worktree 隔离建议 / finishing 步骤

### Kueiku 能力增强（吸收 pm-skills + design.md + writing-plans）
- 新增 7 个方法论类别：产品发现 / 上市策略 / 市场研究 / 数据分析 / AI 交付 / 编程 / 架构优化
- 新增约 40 个方法论 reference 文件（OST / Assumption Mapping / Pretotypes / Mom Test / Product Trio / Opportunity Score / ICE / Product Strategy Canvas / Lean Canvas / Startup Canvas / 6-Part JTBD / Monetization / Pricing / Can't-Won't / Beachhead / ICP / GTM Motions / Growth Loops / Battlecard / TAM-SAM-SOM / Market Segmentation / User Segmentation / User Personas / Cohort / A-B Test / Lean Analytics Metrics / Outcome Roadmap / Strategy Red-Team / User Stories / Job Stories / Shipping Artifacts / Intended-vs-Implemented / Positioning / TDD Red-Green-Refactor / Bite-Sized Plan / Typed Service Contracts / Agent DX CLI Scale 等）
- 增强现有 4 个方法论（North Star / Value Proposition Canvas / RICE / Pre-mortem）

### Diting 能力增强（吸收 12-factor-agents）
- 新增 `review agent` 子维度（Engine A 第 16 维度），含 7 个可检测审核方法：
  Control-Flow Ownership / Prompt Ownership / Context Window Serialization / State Unification / Human-as-Tool / Error Compaction / Intent Dispatch
- 4 个 reference 型提示（F6/F10/F11/F12）

### Tiangang 能力增强
- 新增 Agent 反模式 Semgrep 自定义规则集
- 补齐 test-prompts.json

### Maliang 能力增强（吸收 taste-skill/ui-ux-pro-max-skill/design.md）
- 新增 references/meta/ 下：dials.md / ai-tells.md / rules-priority.md / performance.md / accessibility.md / llm-behavior.md / product-reasoning.md
- 新增 references/commands/redesign.md 子命令
- 新增 references/dimensions/ 下：glass-effect.md / design-systems.md
- 新增 references/framework/motion-skeletons/ 目录
- 新增 references/vocabulary/ 目录（模式词汇库）
- 增强 principles.md（动画动机原则 / 完整交互状态定律 + 来源标注）
- 增强 color.md（WCAG 对比度强制）/ token.md（导出格式）/ design-md.md（Brief Inference + lint + variation engine）/ preview.md（Pre-Flight Check + Pre-Delivery Checklist）

### Pangu 能力增强
- 新增 scripts/init-skill.sh（初始化 skill 仓库本身）
- 新增 scripts/align-skill.sh（存量 skill 渐进式对齐 maliang 模板）
- 新增 templates/skill/ 模板目录（.gitignore / LICENSE / .claude-plugin / .github / README 模板 / skill.json 模板）

### 共享脚本套件
- 新增项目根 script/ 目录，含 install-skill.sh（将 skill 安装到项目级 agent）
- 软链接到 6 个 skill 的 script/ 目录

### .gitignore 优化
- 优化 maliang/.gitignore，添加常见忽略项（.DS_Store / .meta / .vscode / __pycache__ / *.pyc / node_modules / .idea / *.log / .env 等）

## Capabilities

### New Capabilities
- `skill-rename-restructure`: 4 个 skill 重命名 + 5 个 skill 对齐 maliang 模板结构 + 独立 git 仓库初始化
- `specmark-enhancement`: Specmark 新增 clarify/analyze/converge 子命令 + propose/apply 流程增强
- `kueiku-enhancement`: Kueiku 新增 7 类约 40 个方法论 + 增强 4 个现有方法论
- `diting-enhancement`: Diting 新增 review agent 子维度（7 个 agent 专有审核方法）
- `maliang-enhancement`: Maliang 新增设计原则/用户心理学/交互细节/易用性/设计系统方法 5 类约 28 项增强
- `tiangang-enhancement`: Tiangang 新增 Agent 反模式 Semgrep 规则集
- `pangu-enhancement`: Pangu 新增 init-skill.sh / align-skill.sh / templates/skill/
- `shared-script-suite`: 项目根 script/ 共享脚本套件 + 软链接到各 skill

### Modified Capabilities
（无现有 spec 需修改，本次为首次建立 spec）

## Impact

- **目录结构**：5 个 skill 目录改名（openspec→specmark 等），项目根新增 script/ 目录
- **文件变更**：6 个 skill 各自新增 9-10 个模板文件；SKILL.md 多处修改（frontmatter + 内部引用）
- **新增文件**：约 50+ 个 reference 文件（Kueiku 40+ / Diting 7 / Maliang 10+ / Specmark 3）
- **git 仓库**：5 个新独立 git 仓库初始化
- **依赖关系**：各 skill 的 .claude/skills/gitnexus/ 从 maliang 复制
- **命名规范**：文件夹全小写（specmark/kueiku/diting/tiangang/pangu/maliang），文档首字母大写（Specmark/Kueiku/Diting/Tiangang/Pangu/Maliang）
