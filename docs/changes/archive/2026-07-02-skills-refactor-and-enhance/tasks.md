# Tasks — Skills Refactor and Enhance

按顺序执行，每个任务标记 [P] 表示可并行。

## Phase 1: 基础结构（串行）

- [x] [T001] 重命名 4 个 skill 目录：openspec→specmark、methodology→kueiku、review→diting、security-audit→tiangang。使用 `mv` 命令。
- [x] [T002] specmark 的 reference/ 目录改名为 references/。更新 specmark/SKILL.md 内 5 处路径引用（reference/ → references/）。
- [x] [T003] 修改 4 个 SKILL.md frontmatter name 字段：specmark(name: specmark)、kueiku(name: kueiku)、diting(name: diting)、tiangang(name: tiangang)。修改 specmark/SKILL.md 中 11 处命令路径引用（/openspec → /specmark），但保留外部 CLI 引用（openspec new/status/instructions/list 不变）。
- [x] [T004] 5 个 SKILL.md frontmatter 加 license: MIT 字段：specmark、kueiku、diting、tiangang、pangu。

## Phase 2: 模板补齐（并行，每个 skill 一个 subagent）

- [x] [P][T005] **subagent** — specmark 模板补齐：创建 .gitignore（优化版）/ LICENSE(MIT) / README.md(中文) / README_EN.md(英文) / skill.json(8字段,name:specmark,displayName:规格标记) / .claude-plugin/marketplace.json / .github/workflows/release.yml / .claude/skills/gitnexus/(从maliang复制) / openspec/(changes+specs空目录) / test-prompts.json(已有,检查)。frontmatter 已在 T004 加 license。
- [x] [P][T006] **subagent** — kueiku 模板补齐：同 T005 结构，skill.json name:kueiku,displayName:夔牛。补 test-prompts.json（新建，参考 maliang 格式）。
- [x] [P][T007] **subagent** — diting 模板补齐：同 T005 结构，skill.json name:diting,displayName:狄听。已有 test-prompts.json 和 scripts/，检查不覆盖。
- [x] [P][T008] **subagent** — tiangang 模板补齐：同 T005 结构，skill.json name:tiangang,displayName:天罡。补 test-prompts.json（新建）。已有 scripts/。
- [x] [P][T009] **subagent** — pangu 模板补齐：同 T005 结构，skill.json name:pangu,displayName:盘古。已有 scripts/和 templates/和 test-prompts.json。
- [x] [P][T010] **subagent** — maliang .gitignore 优化：在现有 5 行基础上添加 OS/IDE/Python/Node/env/log/Meta 忽略项。

## Phase 3: 能力扩展（并行，每个 skill 一个 subagent）

- [x] [P][T011] **subagent** — specmark 能力扩展：
  - 新增 references/clarify.md（8 分类覆盖扫描，最多 5 问）
  - 新增 references/analyze.md（6 种检测+4 级严重度，只读）
  - 新增 references/converge.md（append-only 收敛，4 种 gap type）
  - 增强 references/propose.md（Task 格式 5 元素 / Self-Review 三项 / No Placeholders / NEEDS CLARIFICATION / Bite-sized TDD）
  - 增强 references/apply.md（前置 critical review / finishing 步骤）
  - 更新 SKILL.md 路由表新增 clarify/analyze/converge
  - 更新阶段协作链路：explore→clarify→propose→apply→converge→archive

- [x] [P][T012] **subagent** — kueiku 能力扩展：
  - 新增 37 个方法论 reference 文件（7 个新类别）：
    - 产品发现(8): opportunity-solution-tree / assumption-mapping / pretotypes / mom-test / product-trio / opportunity-score / ice-framework / experiment-design-library
    - 上市策略(6): beachhead-segment / ideal-customer-profile / gtm-motions / gtm-strategy / growth-loops / competitive-battlecard
    - 市场研究(4): market-sizing / market-segmentation / user-segmentation / user-personas
    - 数据分析(3): cohort-analysis / ab-test-analysis / lean-analytics-metrics
    - AI交付(2): shipping-artifacts / intended-vs-implemented
    - 营销(1): positioning-strategy
    - 编程(2): tdd-red-green-refactor / bite-sized-plan
    - 架构优化(2): typed-service-contracts / agent-dx-cli-scale
    - 战略分析扩展(7): product-strategy-canvas / lean-canvas / startup-canvas / jdb-value-proposition / monetization-strategy / pricing-strategy / cant-wont-defensibility
    - 执行扩展(2): outcome-roadmap / strategy-red-team / user-stories / job-stories
  - 增强 4 个现有文件：north-star.md(三商业游戏+7准则) / value-proposition-canvas.md(对比6-Part JTBD) / rice.md(对比ICE/Opportunity Score) / premortem-counterfactual.md(Tigers/Paper Tigers/Elephants分类)
  - 更新 SKILL.md：新增 7 个类别到路由表，更新方法论总数

- [x] [P][T013] **subagent** — diting 能力扩展：
  - 新增 references/commands/agent.md（review agent 子维度）
  - 含 7 个检测方法：F08 Control-Flow Ownership / F02 Prompt Ownership / F03 Context Window Serialization / F05 State Unification / F07 Human-as-Tool / F09 Error Compaction / F01F04 Intent Dispatch
  - 每个方法含：核心思想/检测信号/严重度/判据来源/修复建议
  - 4 个 reference 型提示（F6/F10/F11/F12）
  - 更新 SKILL.md：Engine A 维度列表新增 agent（第 16 维度）

- [x] [P][T014] **subagent** — maliang 能力扩展：
  - 新增 references/meta/dials.md（Three Dials 系统）
  - 新增 references/meta/ai-tells.md（AI Tells 黑名单）
  - 新增 references/meta/rules-priority.md（10 类规则优先级）
  - 新增 references/meta/performance.md（Core Web Vitals + 硬件加速约束）
  - 新增 references/meta/accessibility.md（WCAG + prefers-reduced-motion 等）
  - 新增 references/meta/llm-behavior.md（LLM 截断研究）
  - 新增 references/meta/product-reasoning.md（161 产品类型推理）
  - 新增 references/commands/redesign.md（Redesign Protocol 子命令）
  - 新增 references/dimensions/glass-effect.md（Apple Liquid Glass）
  - 新增 references/dimensions/design-systems.md（11 个真实设计系统索引）
  - 新增 references/framework/motion-skeletons/（GSAP 三骨架）
  - 新增 references/vocabulary/（模式词汇库 8 大类）
  - 增强 references/meta/principles.md（动画动机原则+完整交互状态定律+来源标注）
  - 增强 references/dimensions/color.md（WCAG 对比度强制）
  - 增强 references/meta/token.md（导出格式 DTCG/Tailwind v3/v4）
  - 增强 references/commands/design-md.md（Brief Inference + lint + variation engine）
  - 增强 references/commands/preview.md（Pre-Flight Check + Pre-Delivery Checklist）

- [x] [P][T015] **subagent** — tiangang 能力扩展：
  - 新增 references/agent-semgrep-rules.md（Agent 反模式 Semgrep 规则集）
  - 含 7 条规则：agent.run(rawText) / Agent(role= / Crew( / Task(expected_output= / langgraph graph / 无显式 while/break / 无 consecutive_errors 熔断
  - 更新 SKILL.md：引用新增的 agent-semgrep-rules

- [x] [P][T016] **subagent** — pangu 能力增强：
  - 新增 scripts/init-skill.sh（初始化 skill 仓库本身，对齐 maliang 模板）
  - 新增 scripts/align-skill.sh（存量 skill 渐进式对齐）
  - 新增 templates/skill/ 模板目录（.gitignore / LICENSE / .claude-plugin/marketplace.json / .github/workflows/release.yml / README.md.template / README_EN.md.template / skill.json.template）
  - 更新 SKILL.md：文档新增 init-skill 和 align-skill 能力

## Phase 4: 共享脚本套件（串行）

- [x] [T017] 创建项目根 script/ 目录。新增 script/install-skill.sh（接收 skill 名称 + 目标 agent 路径，复制/软链接 skill 到目标路径，验证安装）。
- [x] [T018] 为 6 个 skill 创建 script/ 软链接到项目根 script/：maliang/script → ../script、specmark/script → ../script、kueiku/script → ../script、diting/script → ../script、tiangang/script → ../script、pangu/script → ../script。注意：已有 scripts/（复数）的 skill 保留原 scripts/，新增 script/（单数）软链接。

## Phase 5: git 仓库初始化（并行）

- [x] [P][T019] **subagent** — specmark git init + 首次 commit
- [x] [P][T020] **subagent** — kueiku git init + 首次 commit
- [x] [P][T021] **subagent** — diting git init + 首次 commit
- [x] [P][T022] **subagent** — tiangang git init + 首次 commit
- [x] [P][T023] **subagent** — pangu git init + 首次 commit

## Phase 6: 验证（串行）

- [x] [T024] 命名规范验证：grep 所有文件夹名全小写；grep 所有 README 标题首字母大写；grep 所有 skill.json name 全小写；grep 所有 SKILL.md frontmatter name 全小写。
- [x] [T025] 模板完整性验证：对 5 个 skill 逐个检查 9 项模板文件存在性（.gitignore/LICENSE/README.md/README_EN.md/skill.json/.claude-plugin/marketplace.json/.github/workflows/release.yml/.claude/skills/gitnexus/openspec/）。
- [x] [T026] 引用一致性验证：grep specmark/SKILL.md 确认无遗漏的 /openspec 命令路径引用（openspec CLI 引用除外）；grep 确认无 reference/（单数）残留。
- [x] [T027] .gitignore 验证：确认 6 个 skill 的 .gitignore 都含 .DS_Store / .meta / .vscode / __pycache__ / *.pyc / node_modules / .idea / *.log / .env。

## Phase 7: 复盘修正（用户反馈 12 项需求）

### Round 1: 结构修正

- [x] [T028] maliang/references/framework/motion-skeletons 移到 references/ 顶层（framework/ 只放具体框架文档）
- [x] [T030] 中文名修正：diting="谛听"（非"狄听"）、kueiku="鬼谷子"（非"夔牛"）

### Round 2: 文档优化

- [x] [T033] tiangang/SKILL.md description 精简到 ≤200 字符（183 字符）+ 换行修复 + 英文中文化
- [x] [T032] 其余 5 skill（maliang/specmark/kueiku/diting/pangu）换行修复 + 英文中文化
- [x] [T035] kueiku/references/ 按 13 大类分层整理（problem-diagnosis/strategy/product-growth/...）

### Round 3: 字段统一 + 脚本增强

- [x] [T036-C2] 6 个 skill.json 字段统一为 name/description/license/version/author/repo/homepage/tag
- [x] [T036-C3] 6 个 skill .gitignore 添加 changes/ 忽略（specmark git rm --cached changes/）
- [x] [T034] install-skill.sh 增强：增加 qoder agent + generate-commands 子命令

### Round 4: scripts/ 统一 + 独立可用

- [x] [T036-C1] script/ → scripts/ 统一为复数（项目根 + 6 skill）
- [x] [T037] 软链接改文件副本 + install-skill.sh 增加独立 skill 仓库模式识别（is_standalone_skill_repo）

### Round 5: ASCII → mermaid

- [x] [T029] 所有文档 ASCII 图表改 mermaid 语法（中文用双引号包裹；2x2 矩阵用 quadrantChart；文件树/kano 折线图保留）

### Round 6: 安全审查

- [x] [T031] 用 security-audit(tiangang) skill SAST 扫描项目代码安全
  - 修复：install-skill.sh IFS 全局设置改局部 read -ra（24 处）
  - 修复：6 skill release.yml actions/checkout pin 到 SHA
  - 修复：tiangang generate_report.py 优先使用 defusedxml
  - 不修复：pangu/templates/ curl|bash（模板文件，各语言标准安装方式）
  - 不修复：tiangang run_scan.py subprocess shell=True（需大重构，输入受控）

### Round 7: 收尾

- [x] [T038] 确认 .claude/ 目录不进仓库（6 skill .gitignore 均含 .claude；.claude-plugin/ 正确跟踪）
- [x] [T039] 检查所有任务完成 + openspec archive 归档
