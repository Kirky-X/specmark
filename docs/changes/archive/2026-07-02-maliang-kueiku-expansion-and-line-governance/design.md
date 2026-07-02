# Design — maliang+kueiku 能力扩展与行数治理

## 设计原则

1. **先治理后吸收**：先精简现有超标文件，再新增内容。避免新内容加剧超标。
2. **拆分优先于精简**：对于内容价值高的超标文件，优先拆分为多个子文件，而非删减内容。
3. **确定性逻辑显式化**：dial 推断表、Pre-Flight Check 等确定性逻辑必须写成显式表/清单（规则5）。
4. **冲突显性化**：Jobs 方法论与其他方法的冲突在 reference 文件中显式标注边界，不折中混合（规则7）。
5. **导航型骨架**：kueiku 新增 reference 只保留方法论骨架（核心理念 + 适用场景 + 步骤 + 输出模板 + 与其他方法的关系），剥离执行细节。

## Phase A：行数治理设计

### A1. SKILL.md 精简策略

**kueiku 547→200**：
- 当前结构：13 类方法论 × 每类列详细方法列表 = 大量行数
- 精简策略：SKILL.md 只保留路由表（类别→任务类型映射）+ 选用指南 + 子命令路由。每类方法论的详细列表移至 `references/<类别>/index.md`（新建）
- 保留：子命令路由表 / 选用指南表 / 阶段协作链路
- 移除：每类下的方法列表详情（移至 index.md）

**pangu 222→200**：
- 精简策略：合并冗余说明，保留核心 init/align 子命令路由

### A2. description 精简策略

格式：`"<skill 描述 ≤50 字符>。触发：<场景>；<触发词>"`，整体 ≤200 字符。

| skill | 当前字符 | 目标格式 |
|-------|---------|---------|
| maliang | 237 | "前端设计生成 skill。触发：生成高品质前端界面/设计系统/组件" |
| kueiku | 391 | "工作方法论导航。触发：分析/策略/决策/用户研究/结构化思考" |
| diting | 618 | "代码质量套件。触发：review/audit/tech debt/over-engineering" |
| pangu | 844 | "工业级项目 harness 初始化。触发：初始化项目/CI/pre-commit/release" |

### A3. reference 文件拆分策略

**拆分原则**：>400 行的文件按主题拆分为 2-3 个子文件；300-400 行的文件精简冗余。

**maliang 4 个**：
- `commands/design-md.md` 600→拆分：design-md.md（主流程 ≤300）+ design-md-advanced.md（高级特性）
- `dimensions/layout.md` 381→精简：移除冗余示例
- `commands/preview.md` 345→精简：移除冗余说明（B2 会补 Pre-Flight Check）
- `meta/spec-schema.md` 308→精简：移除冗余字段说明

**diting 13 个**：
- `security/examples.md` 1097→拆分为 4 个：examples-owasp.md / examples-injection.md / examples-auth.md / examples-config.md
- `performance/performance-engineer-guide.md` 507→拆分：performance-engineer-guide.md（主流程）+ performance-deep-dive.md（深度分析）
- `simplification/refactoring-patterns.md` 487→拆分：refactoring-patterns.md（模式目录）+ refactoring-techniques.md（技法）
- `quality/code-smells.md` 441→拆分：code-smells.md（目录）+ code-smells-catalog.md（详细目录）
- `architecture/architect-guide.md` 438→拆分：architect-guide.md（主流程）+ architecture-anti-patterns.md（反模式）
- `security/security-fixes.md` 419→拆分：security-fixes.md（修复策略）+ security-fixes-catalog.md（详细修复）
- `security/security-expert-guide.md` 406→精简：移除冗余案例
- `simplification/simplification-guidelines.md` 401→精简：合并重复规则
- `architecture/dependency-analysis.md` 388→精简：移除冗余示例
- `architecture/microservices-compliance.md` 374→精简：移除冗余检查项
- `architecture/design-pattern-review.md` 371→精简：移除冗余模式说明
- `security/pattern-classification.md` 326→精简：合并分类
- `architecture/system-architecture.md` 314→精简：移除冗余图示

## Phase B：maliang 能力扩展设计

### B1. 液态玻璃真实折射（拆分文件）

**`dimensions/glass-effect.md`（精简后 ≤300 行）**：
- 保留：backdrop-filter 基础配方 + 暗色/降级/性能预算
- 移除：过时的"无法复现折射"声明
- 更新：引用 glass-advanced.md 获取高级技术

**`dimensions/glass-advanced.md`（新增，≤300 行）**：
- 第 1 节：SVG `feDisplacementMap` 位移折射（shuding 算法）
  - feDisplacementMap 属性说明（in/in2/scale/xChannelSelector/yChannelSelector）
  - SDF（有符号距离场）算法：roundedRectSDF + smoothStep 生成位移剖面
  - Canvas 生成位移贴图：R=X 位移，G=Y 位移，归一化到 0.5 中心
- 第 2 节：物理参数模型（archisvaze）
  - 双渲染引擎策略：SVG（仅 Chrome）vs WebGL（全浏览器）
  - Snell 定律折射计算：eta = 1/ior，refract 函数
  - 表面函数枚举：convex_squircle / convex_circle / concave / lip
  - 色差（chromatic aberration）：3 通道位移分离
  - 参数表：玻璃厚度/斜面宽度/折射率/缩放比/模糊/镜面/内阴影/外阴影/染色
- 第 3 节：组件参数规格（react/vue）
  - Props→DESIGN.md token 映射：glass.displacement_scale / glass.blur_amount / glass.saturation / glass.aberration / glass.elasticity / glass.mode
  - effect 枚举（仅 mode="shader"）：flowingLiquid / liquidGlass / transparentIce / unevenGlass / mosaicGlass
  - 指令 vs 组件使用决策
- 第 4 节：浏览器支持矩阵 + 降级路径

### B2. 前端 skill 精华吸收

**`vocabulary/hero.md` + `vocabulary/layout.md` 补生产级硬规则**：
- Hero 栈 ≤4 元素（禁 tagline / trust strip / 定价预告 / 功能 bullet）
- Hero 顶部 padding ≤ pt-24 / 标题 ≤2 行 / 副文 ≤20 词 / CTA 可见
- Eyebrow 节制：每 3 节 ≤1 个，机械计数检查
- Zigzag 交替上限：连续 ≤2 个图文分屏
- Split-header 禁令
- Bento 单元数 = 内容数（无空格）
- Section 布局重复禁令：8 节 ≥4 种布局族
- Marquee 单页 ≤1
- CTA 不换行 + 无重复意图

**`meta/dials.md` 补 dial 推断表 + 用例预设表**：
- 6 类信号识别：页面类型 / vibe 词 / 参考信号 / 受众 / 品牌资产 / 静默约束
- 信号→dial 值映射表（VARIANCE/MOTION/DENSITY）
- 用例预设表：landing/dashboard/docs/portfolio/marketing 等

**`commands/preview.md` 补 Pre-Flight Check ~50 项**：
- em-dash 计数（中文场景放宽，只查英文 em-dash）
- eyebrow 计数 / 主题锁 / 色彩锁 / 形状锁 / 对比度
- Hero 适配 / 移动端折叠 / 动画动机 / Core Web Vitals

**`vocabulary/micro-interactions.md` 补高端技法**：
- Double-Bezel（Doppelrand）：外壳 ring-1 + padding + 大圆角，内核 inset 高光 + 同心圆角公式 `rounded-[calc(2rem-0.375rem)]`
- Button-in-Button：箭头图标嵌套圆形 wrapper，hover 对角位移 + scale-105
- Fluid Island 导航：浮动玻璃 pill + 汉堡 morph X + staggered mask reveal
- Magnetic button：group + active:scale-[0.98] + 内圈对角位移
- Scroll interpolation：translate-y-16 blur-md opacity-0 → 0，800ms+
- 自定义 cubic-bezier `ease-[cubic-bezier(0.32,0.72,0,1)]` 禁 linear/ease-in-out

**`commands/design-md.md` 补 Design Read + Working Model**：
- Design Read 一行：`Reading this as: <page kind> for <audience>, with <vibe> language, leaning toward <design system>`
- Working Model 三件事：visual thesis / content plan / interaction thesis

**`dimensions/design-systems.md` 补 brief→官方包映射表**：
- Fluent UI / Carbon / Polaris / Atlaskit / Primer / GOV.UK / USWDS / Bootstrap / Radix Themes / shadcn / Tailwind
- 诚实规则：不手写复刻官方 CSS
- 一项目一系统

## Phase C：kueiku 能力扩展设计

### C1. 新增类别

**`product-philosophy/`（4 文件）**：
- `focus-as-no.md`：聚焦即说不（激进减法，4 格矩阵案例）
  - 边界标注：反对"问要什么然后照做"，不反对"深度理解任务"（与 Mom Test 互补）
- `whole-widget.md`：端到端控制（垂直整合产品架构决策）
- `technology-meets-humanities.md`：技术与人文交汇（产品评估维度）
- `invisible-perfection.md`：看不见的地方也要完美（工艺美学原则）

**`leadership/`（2 文件）**：
- `reality-distortion-field.md`：RDF
  - 局限标注：Jobs 延误癌症手术 9 个月反例
  - 适用场景：推动团队突破自我设限
  - 不适用场景：技术可行性判断 / 风险评估 / 医疗决策
- `a-player-density.md`：A Player 自我增强（人才密度原则）

### C2. 财务分析类别

**`financial-analysis/`（4 文件）**：
- `dupont.md`：杜邦分析（ROE 拆解 = 净利率 × 资产周转率 × 权益乘数）
- `dcf.md`：现金流折现估值
- `comparable-company.md`：可比公司分析
- `eva.md`：经济增加值（EVA = NOPAT - 资本成本 × 投入资本）

### C3. 研究方法论类别

**`research-methodology/`（1 文件）**：
- `systematic-research-process.md`：
  - 5 步流程：明确问题 → 拆解子主题 → 收集信息 → 综合发现 → 记录来源
  - 来源可信度 5 级：Peer-reviewed > Official reports > News > Expert commentary > General websites
  - 输出结构：Executive Summary → Key Findings → Detailed Analysis → Areas of Consensus → Areas of Debate → Sources → Gaps
  - 辩证分析结构（Consensus vs Debate）是 kueiku 现有方法都缺失的维度

### C4. 扩充现有类别

**`strategy/`（6 文件）**：
- `porter-diamond-model.md`：国家竞争优势决定因素（生产要素/需求条件/相关产业/企业战略）
- `ge-mckinsey-matrix.md`：9 格矩阵（BCG 进阶版）
- `strategic-group-mapping.md`：战略群组图
- `value-chain-analysis.md`：Porter 价值链（主活动+支持活动）
- `benchmarking.md`：对标分析
- `product-life-cycle.md`：产品生命周期（导入/成长/成熟/衰退）

**`market-research/`（3 文件）**：
- `stp-analysis.md`：Segmentation-Targeting-Positioning
- `perceptual-mapping.md`：品牌感知图
- `technology-adoption-lifecycle.md`：技术采纳生命周期（跨越鸿沟）

**`data-analysis/`（1 文件）**：
- `rfm-model.md`：Recency-Frequency-Monetary 客户价值细分

**`user-research/`（2 文件）**：
- `consumer-decision-journey.md`：消费者决策旅程（与 Customer Journey 互补：CDJ 是决策路径，CJM 是全旅程）
- `maslow-hierarchy.md`：马斯洛需求层次

**`industry-analysis/`（2 文件，新类别）**：
- `industry-value-chain.md`：行业价值链
- `gartner-hype-cycle.md`：技术成熟度曲线

**`structured-thinking/`（3 文件）**：
- `framework-selection.md`：Framework Selection 元方法论（5 原则：Domain-First / Complementary / Depth over Breadth / Data-Feasible / Explicit Mapping）
- `connecting-dots.md`：连点成线（直觉决策原则）
- `reframe-and-elevate.md`：把问题升维（谈判/沟通策略）

**`decision-making/`（1 文件）**：
- `death-filter.md`：死亡过滤器（存在主义决策过滤器）

### C5. 冲突处理

| 冲突 | 处理方式 | 实现位置 |
|------|---------|---------|
| Jobs "不问用户要什么" vs 用户中心 | 标注边界，不折中 | focus-as-no.md 显式说明 |
| RDF vs 风险审视 | 标注局限，限定场景 | reality-distortion-field.md 显式说明 |
| 二元判断 vs 结构化分析 | 标注为评价阶段工具 | product-philosophy/ 各文件注记 |
| TAM-SAM-SOM 重复 | 合并到 market-sizing.md | 不创建新文件 |
| AARRR/JTBD 重复 | 不重复创建 | framework-selection.md 引用已有 |
| 导航型 vs 执行型 | 只保留方法论骨架 | 所有新 reference 遵循骨架格式 |

### kueiku SKILL.md 更新

新增 4 类别到路由表：
- product-philosophy（4 文件）
- leadership（2 文件）
- financial-analysis（4 文件）
- research-methodology（1 文件）
- industry-analysis（2 文件，从 strategy 拆分）

类别总数：13 → 18（新增 5 类别）
方法论总数：74 → 99（新增 25 方法论）

## 验证标准

- [ ] 所有 SKILL.md ≤200 行
- [ ] 所有 reference ≤300 行
- [ ] 所有 description ≤200 字符（skill 描述 ≤50 字符）
- [ ] maliang glass-effect.md + glass-advanced.md 完成
- [ ] maliang 6 个 reference 文件增强
- [ ] kueiku 新增 5 类别 + 25 方法论文件
- [ ] kueiku SKILL.md 路由表更新（13→18 类别）
- [ ] 所有冲突显式标注边界
