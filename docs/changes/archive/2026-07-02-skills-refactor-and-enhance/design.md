# Design — Skills Refactor and Enhance

## Overview

本设计文档描述如何将 6 个 skill 统一到 maliang 模板结构，重命名 4 个 skill，并基于 temp/ 分析结果扩展各 skill 能力。执行策略采用**分阶段并行 subagent** 模式，避免上下文污染。

## Key Design Decisions

### D1: 命名规范

| 维度 | 规则 | 示例 |
|------|------|------|
| 文件夹名 | 全小写 | specmark / kueiku / diting / tiangang / pangu / maliang |
| SKILL.md frontmatter name | 全小写 | `name: specmark` |
| 文档标题/README 标题 | 首字母大写 | Specmark / Kueiku / Diting / Tiangang / Pangu / Maliang |
| skill.json displayName | 中文名 | 马良（maliang 已有）/ 规格标记（specmark）/ 夔牛（kueiku）/ 狄听（diting）/ 天罡（tiangang）/ 盘古（pangu）|
| 命令路径 | 全小写 | `/specmark propose` / `/kueiku` / `/diting security` |

**命名由来**：
- Specmark = Spec（规格）+ Mark（标记），规格驱动变更的标记
- Kueiku = 夔牛（kuí niú），《山海经》中独脚神兽，象征方法论的独特视角
- Diting = 狄听，谛听的谐音，象征审查之耳
- Tiangang = 天罡，三十六天罡星，象征安全护卫
- Pangu = 盘古，开天辟地，象征项目初始化
- Maliang = 马良，神笔马良，象征设计创造

### D2: 目录结构对齐策略

每个 skill 对齐到 maliang 模板结构：
```
<skill-name>/
├── .claude/skills/gitnexus/     # 从 maliang 复制
├── .claude-plugin/marketplace.json
├── .github/workflows/release.yml
├── .gitignore                   # 优化后的通用版
├── LICENSE                      # MIT
├── openspec/                    # 含 changes/ + specs/
├── README.md                    # 中文
├── README_EN.md                 # 英文
├── references/                  # 复数（openspec 的 reference/ 需改名）
├── scripts/                     # 各 skill 特有脚本
├── skill.json
├── SKILL.md
├── test-prompts.json
└── (各 skill 特有目录)
```

### D3: .gitignore 优化版

基于 maliang 现有 5 行 + 常见忽略项：
```
# Skill 运行时
.claude
.venv
openspec
temp
.gitnexus

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE
.vscode
.idea
*.swp
*.swo
*~

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 环境变量
.env
.env.local
.env.*.local

# 日志
*.log

# Meta
.meta
```

### D4: 执行策略 — 分阶段并行 subagent

```
Phase 1: 基础结构（串行，因为后续依赖）
  ├─ 1.1 重命名 4 个 skill 目录
  ├─ 1.2 openspec→specmark 的 reference/ → references/ 改名
  └─ 1.3 修改 4 个 SKILL.md frontmatter name + specmark 内部引用

Phase 2: 模板补齐（并行，每个 skill 独立）
  ├─ 2.1 specmark 模板补齐（subagent A）
  ├─ 2.2 kueiku 模板补齐（subagent B）
  ├─ 2.3 diting 模板补齐（subagent C）
  ├─ 2.4 tiangang 模板补齐（subagent D）
  ├─ 2.5 pangu 模板补齐（subagent E）
  └─ 2.6 maliang .gitignore 优化（subagent F）

Phase 3: 能力扩展（并行，每个 skill 独立）
  ├─ 3.1 specmark 能力扩展（subagent A）
  ├─ 3.2 kueiku 能力扩展（subagent B）
  ├─ 3.3 diting 能力扩展（subagent C）
  ├─ 3.4 maliang 能力扩展（subagent D）
  ├─ 3.5 tiangang 能力扩展（subagent E）
  └─ 3.6 pangu 能力扩展（subagent F）

Phase 4: 共享脚本套件（串行）
  ├─ 4.1 创建项目根 script/install-skill.sh
  └─ 4.2 软链接到 6 个 skill 的 script/

Phase 5: git 仓库初始化（并行）
  └─ 5.1-5.5 五个 skill 各自 git init + 首次 commit

Phase 6: 验证（串行）
  ├─ 6.1 命名规范验证
  ├─ 6.2 模板完整性验证
  └─ 6.3 引用一致性验证
```

### D5: specmark 重命名的关键约束

openspec SKILL.md 中 "openspec" 有双重含义：
- 指代 skill 本身（frontmatter name、命令路径 `/openspec`、目录路径）→ **改为 specmark**
- 指代外部 openspec CLI 工具（`openspec new` / `openspec status` 等）→ **保持不变**

判断标准：如果 "openspec" 后面跟的是 CLI 子命令（new/status/instructions/list），则保持不变；如果是 `/openspec`（skill 调用路径）或 `openspec/SKILL.md`（目录引用），则改为 specmark。

### D6: Kueiku 方法论文件命名规范

新增 reference 文件使用 kebab-case：
- `opportunity-solution-tree.md`
- `assumption-mapping.md`
- `pretotypes.md`
- `mom-test.md`
- `product-trio.md`
- `opportunity-score.md`
- `ice-framework.md`
- `product-strategy-canvas.md`
- `lean-canvas.md`
- `startup-canvas.md`
- `jdb-value-proposition.md`
- `monetization-strategy.md`
- `pricing-strategy.md`
- `cant-wont-defensibility.md`
- `beachhead-segment.md`
- `ideal-customer-profile.md`
- `gtm-motions.md`
- `gtm-strategy.md`
- `growth-loops.md`
- `competitive-battlecard.md`
- `market-sizing.md`
- `market-segmentation.md`
- `user-segmentation.md`
- `user-personas.md`
- `cohort-analysis.md`
- `ab-test-analysis.md`
- `lean-analytics-metrics.md`
- `outcome-roadmap.md`
- `strategy-red-team.md`
- `user-stories.md`
- `job-stories.md`
- `shipping-artifacts.md`
- `intended-vs-implemented.md`
- `positioning-strategy.md`
- `tdd-red-green-refactor.md`
- `bite-sized-plan.md`
- `typed-service-contracts.md`
- `agent-dx-cli-scale.md`

### D7: Diting review agent 子维度设计

新增 `references/commands/agent.md`，含 7 个检测方法。每个检测方法的结构：
```
### F0X: <名称>
- **核心思想**: <一句话>
- **检测信号**: <grep 模式 / 代码特征>
- **严重度**: HIGH / MID
- **判据来源**: 12-factor-agents spec.md
- **修复建议**: <一句话>
```

### D8: 共享脚本套件设计

项目根 `script/install-skill.sh` 功能：
1. 接收参数：skill 名称 + 目标 agent 路径（如 `~/.trae-cn/skills/` 或 `~/.claude/skills/`）
2. 将 skill 目录复制（或软链接）到目标路径
3. 验证安装结果

软链接策略：各 skill 的 `script/` 目录软链接到项目根 `script/`，避免重复。

## Trade-offs Considered

### T1: 一次性全量变更 vs 分批变更
- **选择**：一次性全量变更，但分阶段执行
- **原因**：各 skill 之间有依赖（gitnexus 从 maliang 复制、命名规范需统一），分批会导致中间状态不一致

### T2: 方法论全量新增 vs 精选新增
- **选择**：全量新增（约 40 个），但每个文件保持精简（200-400 字）
- **原因**：subagent 分析已过滤工具类/重复类，剩余的都是独立方法论；用户偏好详细模板

### T3: git 仓库初始化时机
- **选择**：在所有文件变更完成后（Phase 5）才 git init
- **原因**：避免变更过程中 git 状态干扰；确保首次 commit 是干净的最终状态

### T4: openspec CLI 引用保持不变
- **选择**：保留 `openspec new` / `openspec status` 等外部 CLI 引用
- **原因**：openspec CLI 是独立的外部工具，skill 重命名不影响 CLI 工具名

## Risks

1. **R1: specmark 内部引用遗漏** — SKILL.md 中有 11 处需改的引用，可能遗漏。缓解：Phase 6 验证阶段用 grep 全文搜索
2. **R2: gitnexus 复制后路径失效** — .claude/skills/gitnexus/ 内的 SKILL.md 可能有 maliang 特定路径。缓解：复制后检查并适配
3. **R3: 方法论文件质量参差** — 40 个文件由 subagent 并行生成，质量可能不均。缓解：每个文件遵循统一模板结构
4. **R4: 软链接跨文件系统失效** — script/ 软链接在不同挂载点可能失效。缓解：使用相对路径软链接
