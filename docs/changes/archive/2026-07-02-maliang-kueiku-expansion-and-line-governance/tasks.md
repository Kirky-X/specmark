# Tasks — maliang+kueiku 能力扩展与行数治理

按顺序执行，每个任务标记 [P] 表示可并行。

## Phase A：行数治理（先治理后吸收）

### A1. SKILL.md 精简（串行）

- [x] [T001] kueiku/SKILL.md 547→200：13 类方法论的详细列表移至 references/<类别>/index.md（新建 13 个 index.md），SKILL.md 只保留路由表 + 选用指南 + 子命令路由
- [x] [T002] pangu/SKILL.md 222→200：精简冗余说明，合并重复段落

### A2. description 精简（并行，每个 skill 一个 subagent）

- [x] [P][T003] **subagent** — maliang description 237→≤200：skill 描述 ≤50 字符 + 触发场景和触发词
- [x] [P][T004] **subagent** — kueiku description 391→≤200：skill 描述 ≤50 字符 + 触发场景和触发词
- [x] [P][T005] **subagent** — diting description 618→≤200：skill 描述 ≤50 字符 + 触发场景和触发词
- [x] [P][T006] **subagent** — pangu description 844→≤200：skill 描述 ≤50 字符 + 触发场景和触发词

### A3. reference 文件拆分/精简（并行，maliang + diting）

- [x] [P][T007] **subagent** — maliang 4 个超标 reference 拆分/精简：
  - commands/design-md.md 600→拆分：design-md.md（主流程 ≤300）+ design-md-advanced.md（高级特性）
  - dimensions/layout.md 381→精简
  - commands/preview.md 345→精简（保留空间给 B2 的 Pre-Flight Check）
  - meta/spec-schema.md 308→精简
- [x] [P][T008] **subagent** — diting 13 个超标 reference 拆分/精简：
  - security/examples.md 1097→拆分 4 个
  - performance/performance-engineer-guide.md 507→拆分 2 个
  - simplification/refactoring-patterns.md 487→拆分 2 个
  - quality/code-smells.md 441→拆分 2 个
  - architecture/architect-guide.md 438→拆分 2 个
  - security/security-fixes.md 419→拆分 2 个
  - security/security-expert-guide.md 406→精简
  - simplification/simplification-guidelines.md 401→精简
  - architecture/dependency-analysis.md 388→精简
  - architecture/microservices-compliance.md 374→精简
  - architecture/design-pattern-review.md 371→精简
  - security/pattern-classification.md 326→精简
  - architecture/system-architecture.md 314→精简

## Phase B：maliang 能力扩展（并行，B1 + B2）

### B1. 液态玻璃真实折射

- [x] [P][T009] **subagent** — maliang 液态玻璃增强：
  - 精简 dimensions/glass-effect.md（移除过时声明，保留基础配方 ≤300 行）
  - 新增 dimensions/glass-advanced.md（SVG feDisplacementMap + SDF 算法 + 物理参数模型 + 组件参数规格 + effect 枚举 + 浏览器支持矩阵）
  - 参考 temp/liquid-glass-refs/ 下 4 个仓库

### B2. 前端 skill 精华吸收（并行，6 个文件）

- [x] [P][T010] **subagent** — maliang vocabulary 增强：
  - vocabulary/hero.md + vocabulary/layout.md 补生产级硬规则（Hero 栈 ≤4 / Eyebrow 节制 / Zigzag 上限 / Split-header 禁令 / Bento 单元数 / Section 布局重复禁令 / Marquee 单页 ≤1）
- [x] [P][T011] **subagent** — maliang meta/dials.md 补推断表：
  - 6 类信号识别 + 信号→dial 值映射表 + 用例预设表
- [x] [P][T012] **subagent** — maliang commands/preview.md 补 Pre-Flight Check：
  - ~50 项机械清单（em-dash 中文场景放宽 / eyebrow 计数 / 主题锁 / 色彩锁 / 形状锁 / 对比度 / Hero 适配 / Core Web Vitals）
- [x] [P][T013] **subagent** — maliang vocabulary/micro-interactions.md 补高端技法：
  - Double-Bezel / Button-in-Button / Fluid Island / Magnetic button / Scroll interpolation / cubic-bezier
- [x] [P][T014] **subagent** — maliang commands/design-md.md 补 Design Read + Working Model：
  - Design Read 一行检查点 + visual thesis / content plan / interaction thesis 三件事
- [x] [P][T015] **subagent** — maliang dimensions/design-systems.md 补 brief→包映射表：
  - Fluent UI / Carbon / Polaris / Atlaskit / Primer / GOV.UK / USWDS / Bootstrap / Radix Themes / shadcn / Tailwind

## Phase C：kueiku 能力扩展（并行，C1-C4）

### C1. 新增产品哲学 + 领导力类别

- [x] [P][T016] **subagent** — kueiku product-philosophy/ 新增 4 文件：
  - focus-as-no.md（激进减法 + 边界标注：反对"问要什么然后照做"，不反对"深度理解任务"）
  - whole-widget.md（垂直整合产品架构决策）
  - technology-meets-humanities.md（产品评估维度）
  - invisible-perfection.md（工艺美学原则）
- [x] [P][T017] **subagent** — kueiku leadership/ 新增 2 文件：
  - reality-distortion-field.md（局限标注：Jobs 延误癌症 9 个月反例 / 适用：推动团队突破 / 不适用：技术可行性/风险/医疗）
  - a-player-density.md（人才密度原则）

### C2. 新增财务分析类别

- [x] [P][T018] **subagent** — kueiku financial-analysis/ 新增 4 文件：
  - dupont.md（ROE 拆解）
  - dcf.md（现金流折现）
  - comparable-company.md（可比公司分析）
  - eva.md（经济增加值）

### C3. 新增研究方法论类别

- [x] [P][T019] **subagent** — kueiku research-methodology/ 新增 1 文件：
  - systematic-research-process.md（5 步流程 + 来源评估 5 级 + 输出结构 + Consensus vs Debate 辩证分析）

### C4. 扩充现有类别（并行，6 个 subagent）

- [x] [P][T020] **subagent** — kueiku strategy/ 新增 6 文件：
  - porter-diamond-model.md / ge-mckinsey-matrix.md / strategic-group-mapping.md / value-chain-analysis.md / benchmarking.md / product-life-cycle.md
- [x] [P][T021] **subagent** — kueiku market-research/ 新增 3 文件：
  - stp-analysis.md / perceptual-mapping.md / technology-adoption-lifecycle.md
- [x] [P][T022] **subagent** — kueiku data-analysis/ + user-research/ 新增 3 文件：
  - data-analysis/rfm-model.md / user-research/consumer-decision-journey.md / user-research/maslow-hierarchy.md
- [x] [P][T023] **subagent** — kueiku industry-analysis/ 新增 2 文件（新类别）：
  - industry-value-chain.md / gartner-hype-cycle.md
- [x] [P][T024] **subagent** — kueiku structured-thinking/ 新增 3 文件：
  - framework-selection.md（元方法论 5 原则）/ connecting-dots.md / reframe-and-elevate.md
- [x] [P][T025] **subagent** — kueiku decision-making/ 新增 1 文件：
  - death-filter.md（存在主义决策过滤器）

### C5. kueiku SKILL.md 路由表更新

- [x] [T026] kueiku/SKILL.md 更新：新增 5 类别到路由表（product-philosophy / leadership / financial-analysis / research-methodology / industry-analysis），方法论总数 74→99

## Phase D：验证 + 归档

- [x] [T027] 行数验证：所有 SKILL.md ≤200 / reference ≤300 / description ≤200
- [x] [T028] git commit 6 个 skill 仓库
- [x] [T029] openspec archive 归档变更

## 范围扩展：hap-dev 行数治理（验证发现的技术债，非本变更原始范围）

> 决策记录：T027 验证发现 hap-dev 3 个超标（description 351 字符 + fix.md 322 行 + any_type_errors.md 433 行）。用户原话"所有 SKILL.md"为泛指，端到端治理原则下直接修复，不另起变更。

- [x] [P][T030] hap-dev description 351→≤200：skill 描述 ≤50 字符 + 触发场景和触发词
- [x] [P][T031] hap-dev/references/commands/fix.md 322→≤300：精简冗余说明
- [x] [P][T032] hap-dev/references/error-fixes/any_type_errors.md 433→≤300：拆分为主文件 + any-type-examples.md
