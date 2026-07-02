# Proposal — maliang+kueiku 能力扩展与行数治理

## 变更范围

本变更同时解决三类问题：(1) maliang 吸收液态玻璃真实折射技术 + 4 个前端 skill 精华；(2) kueiku 吸收 steve-jobs-perspective / deep-research / consulting-analysis 三 skill 的方法论资产；(3) 6 个 skill 的行数合规治理（SKILL.md ≤200 行 / reference ≤300 行 / description ≤200 字符）。

## Why

**maliang 能力缺口**：
- `dimensions/glass-effect.md` 当前仅覆盖 `backdrop-filter` 模糊近似，且文件中明确写"Web 端无法完全复现折射"——但 4 个开源仓库（shuding/liquid-glass 等）证明 SVG `feDisplacementMap` + SDF 算法可在 Chrome 实现真实边缘折射，WebGL 可全浏览器实现。前提已过时。
- vocabulary/ 只有模式命名，缺生产级硬规则（Hero 栈 ≤4 元素 / Eyebrow 节制机械计数 / Zigzag 上限等）。
- meta/dials.md 只有 dial 定义，缺"如何从 brief 推断 dial 值"的确定性映射表（违反规则5：确定性逻辑禁止交给模型）。
- commands/preview.md 缺机械式 Pre-Flight Check 交付前门禁。
- vocabulary/micro-interactions.md 缺高端组件工艺（Double-Bezel / Button-in-Button / Fluid Island / Magnetic button）。

**kueiku 能力缺口**：
- 完全无"产品哲学"类别——Jobs 的聚焦即说不 / 端到端控制 / 技术与人文交汇 / 看不见的完美是独特视角。
- 完全无"领导力"类别——RDF / A Player 密度有滥用风险但有独特价值（用户决策：吸收并标注局限）。
- 完全无"财务分析"类别——DuPont / DCF / Comparable Company / EVA 是咨询必备。
- 完全无"通用研究方法论"类别——deep-research 的 5 步系统化研究流程填补明显空白。
- 缺失 12-18 个经典分析框架（Porter's Diamond / STP / Value Chain / Gartner Hype / TALC / GE-McKinsey / RFM / CDJ 等）。
- 缺 Framework Selection 元方法论（如何选框架的 5 原则）。

**行数治理**：
- kueiku SKILL.md 547 行（超标 173%），pangu SKILL.md 222 行（超标 11%）。
- 4 个 description 超标：maliang 237 / kueiku 391 / diting 618 / pangu 844 字符（限 200）。
- 17 个 reference 文件超 300 行：maliang 4 个（design-md 600 / layout 381 / preview 345 / spec-schema 308），diting 13 个（最大 examples 1097）。

## What

### Phase A：行数治理（先治理后吸收，避免新内容加剧超标）

**A1. SKILL.md 精简**：
- kueiku 547→200：将 13 类方法论的路由详情移至 references/ 下的索引文件，SKILL.md 只保留路由表 + 选用指南
- pangu 222→200：精简冗余说明

**A2. description 精简**（≤200 字符，skill 描述 ≤50 字符，剩下是触发场景和触发词）：
- maliang / kueiku / diting / pangu 4 个

**A3. reference 文件精简/拆分**（≤300 行）：
- maliang 4 个：design-md.md（600→拆分）/ layout.md（381→精简）/ preview.md（345→精简）/ spec-schema.md（308→精简）
- diting 13 个：examples.md（1097→拆分）/ performance-engineer-guide.md（507→拆分）/ refactoring-patterns.md（487→拆分）/ code-smells.md（441→拆分）/ architect-guide.md（438→拆分）/ security-fixes.md（419→拆分）/ security-expert-guide.md（406→拆分）/ simplification-guidelines.md（401→拆分）/ dependency-analysis.md（388→拆分）/ microservices-compliance.md（374→拆分）/ design-pattern-review.md（371→拆分）/ pattern-classification.md（326→拆分）/ system-architecture.md（314→拆分）

### Phase B：maliang 能力扩展

**B1. 液态玻璃真实折射**（用户决策：引入 SVG+WebGL，拆分文件）：
- `dimensions/glass-effect.md` 保持 backdrop-filter 基础配方（精简到 ≤300 行）
- 新增 `dimensions/glass-advanced.md`：SVG `feDisplacementMap` + SDF 算法（shuding）+ 物理参数模型 + 双引擎降级（archisvaze）+ 组件参数规格（react/vue）+ effect 枚举

**B2. 前端 skill 精华吸收**：
- `vocabulary/hero.md` + `vocabulary/layout.md` 补生产级硬规则（Hero 栈 ≤4 / Eyebrow 节制 / Zigzag 上限 / Split-header 禁令 / Bento 单元数 / Section 布局重复禁令 / Marquee 单页 ≤1）
- `meta/dials.md` 补 dial 推断表 + 用例预设表（信号→dial 值映射，确定性逻辑）
- `commands/preview.md` 补 Pre-Flight Check ~50 项机械清单（em-dash 中文场景放宽）
- `vocabulary/micro-interactions.md` 补高端技法（Double-Bezel / Button-in-Button / Fluid Island / Magnetic button / Scroll interpolation）
- `commands/design-md.md` 补 Design Read 前置检查点 + Working Model 三件事
- `dimensions/design-systems.md` 补 brief→官方包映射表

### Phase C：kueiku 能力扩展

**C1. 新增 2 类别**（用户决策：引入产品哲学 + 领导力）：
- `product-philosophy/`：focus-as-no.md / whole-widget.md / technology-meets-humanities.md / invisible-perfection.md
- `leadership/`：reality-distortion-field.md（标注局限：Jobs 延误癌症案例）/ a-player-density.md

**C2. 新增财务分析类别**：
- `financial-analysis/`：dupont.md / dcf.md / comparable-company.md / eva.md

**C3. 新增研究方法论类别**：
- `research-methodology/`：systematic-research-process.md（5 步流程 + 来源评估 + 输出结构）

**C4. 扩充现有类别**（12-18 个新框架）：
- `strategy/`：porter-diamond-model.md / ge-mckinsey-matrix.md / strategic-group-mapping.md / value-chain-analysis.md / benchmarking.md / product-life-cycle.md
- `market-research/`：stp-analysis.md / perceptual-mapping.md / technology-adoption-lifecycle.md
- `data-analysis/`：rfm-model.md
- `user-research/`：consumer-decision-journey.md / maslow-hierarchy.md
- `industry-analysis/`：industry-value-chain.md / gartner-hype-cycle.md
- `structured-thinking/`：framework-selection.md（元方法论）/ connecting-dots.md / reframe-and-elevate.md
- `decision-making/`：death-filter.md

**C5. 冲突处理**（规则7）：
- Jobs "不问用户要什么"：在 focus-as-no.md 标注边界（反对"问要什么然后照做"，不反对"深度理解任务"）
- TAM-SAM-SOM / AARRR / JTBD：合并不重复创建
- 导航型 vs 执行型：只保留方法论骨架（核心理念 + 适用场景 + 步骤 + 输出模板 + 与其他方法的关系）

## Non-Goals

- 不修改 maliang 的 framework/ 目录下组件 API 文档（已稳定）
- 不修改 specmark / tiangang 的 reference 文件（均合规）
- 不引入"沟通表达"类别（kueiku 严格限定在分析/决策/研究领域）
- 不升级 vocabulary 为带 schema 的实现规格库（保持轻量命名，maliang 已有 framework/ 放实现规格）
- 不吸收 steve-jobs 的表达 DNA 作为独立类别（可并入 product-philosophy 的注记）

## 决策记录

| 决策点 | 用户选择 | 理由 |
|--------|---------|------|
| maliang glass-effect.md | 引入 SVG+WebGL，拆分文件 | 4 仓库证明技术可行，前提已过时 |
| kueiku 新类别 | 引入产品哲学 + 领导力 | Jobs 视角独特，RDF 标注局限后有价值 |
| kueiku RDF | 吸收并标注局限 | 领导力工具有独特价值，显式标注反例 |
| 执行顺序 | 先治理后吸收 | 避免新内容加剧超标 |
