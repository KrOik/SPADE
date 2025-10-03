# SPADE: An Intelligent Software Platform for Antimicrobial Peptide Discovery

## 1. Project Vision and Motivation

SPADE serves researchers and industry R&D teams who need dependable antimicrobial peptide (AMP) data that can be queried quickly and applied directly in discovery workflows, bringing curated entries, clear structures and practical filters together so everyday questions can be answered without wrestling with format inconsistencies or scattered sources.

The index covers more than 46,000 peptides, cross‑referenced from PubMed and peer‑reviewed literature, and consolidated into a single schema that preserves provenance while standardizing key fields to support consistent queries.

Data quality is maintained through a streamlined yet rigorous pipeline that combines human judgment and automation: records are cross‑checked across sources and harmonized by manual curation when fields conflict, duplicates are removed by exact sequence and normalized name matching with additional near‑duplicate flags from edit‑distance checks, and each release undergoes stratified random sampling to verify correctness and relevance; we publish per‑release quality indicators—manual cross‑check counts, automated deduplication rate, and sampling coverage—together with the index so users can see how the dataset is maintained over time.

To match common usage habits, the website supports Chinese, English, Japanese, German and Spanish, and the search interface keeps interactions consistent with a left‑side panel for filters and a results table that updates immediately as conditions change; filters name the fields users care about—ID, name, sequence length, activity type and target organism, physicochemical attributes such as net charge and hydrophobicity, and predicted structural features—so typical queries can be expressed in one pass.

A typical combination might target antifungal activity against Candida albicans with net charge above +2 and a hydrophobicity range suited to membrane interaction, and the operational path keeps analysis close to the task by setting conditions on the Search page, reading the updated results table, and opening the peptide’s card to examine consolidated details in a single view.

## 2. A Guided Tour of the SPADE Platform

SPADE is organized into modules that mirror a typical discovery workflow. Each page focuses on a single task and keeps navigation simple.

- Home Page (home.html): overview of the platform and entry points to core modules.

![SPADE Home Page](source/img/usage/mainpage.jpg "Suggested Image: A screenshot of the SPADE home page, highlighting the main navigation and mission statement.")

- Search Page (search.html): fast, multi-dimensional filtering over a curated index of >46,000 peptides. Filters cover basic properties (ID, name, length), activity types and target organisms, physicochemical attributes (charge, hydrophobicity), and predicted structural features.

![SPADE Search Page](source/img/usage/mainpage.jpg "Suggested Image: A screenshot of the Search page, showing the filter panel on the left and the results table on the right.")

- Peptide Card (peptide_card.html): consolidated view of a single peptide—sequence, properties, activities, structure, and literature links.

- AMP Visualization (amp_visualization.html): graphical views such as hydrophobicity profiles and 2D structure predictions to aid interpretation.

![SPADE Peptide Card and Visualization](source/img/usage/mainpage.jpg "Suggested Image: A composite image showing a Peptide Card on one side and a visualization (e.g., hydrophobicity plot) on the other.")

- Tools Page (tools.html): links to internal scripts and vetted external tools for alignment, structure prediction, toxicity analysis, etc.

- Statistics Page (Statistics.html): interactive charts summarizing global distributions (lengths, activity types, target organisms).

![SPADE Tools and Statistics Pages](source/img/usage/mainpage.jpg "Suggested Image: A composite image showing the Tools page and an example chart from the Statistics page.")

## 3. Design Philosophy and Architectural Overview

The frontend is a static site (HTML/CSS/vanilla JS). For specific processing tasks, we use a lightweight Flask backend. This keeps the UI fast and portable, suitable for simple hosting or CDNs.

For search, SPADE relies on a pre-compiled JSON index (peptide_index.json) instead of a relational database.
- Rationale: fewer dependencies, simpler deployment, and high portability; suitable for labs without dedicated IT support.
- Trade-off: database engines offer richer queries but add complexity. For filter-based discovery, a single JSON object with efficient client-side filtering is sufficient.

Pages are modular and loosely coupled. New features can be added by introducing a dedicated page and wiring it into navigation without disturbing existing modules.

Advanced components (e.g., RAG + Neon database) are provided on an as-needed schedule due to resource demands. To control misuse and cost, continuous public access is not offered.

## 4. User Guide: Getting Started with SPADE

Step 1: Multi-Dimensional Search
1) Open the Search page from the main navigation.
2) Use the left-side filter panel (Basic, Activity, Structure) to set conditions—for example: Antifungal activity targeting Candida albicans, net charge > +2.
3) Results update in real time on the right. Refine conditions iteratively.

Step 2: Analyze a Specific Peptide
1) Locate a peptide of interest in the results.
2) Click “View” in the Action column to open its Peptide Card.
3) Review sequence, properties, activities, structure, and source references.

Step 3: Visual Inspection
1) Click “Visualize” to open plots such as hydrophobicity and 2D structural predictions.
2) Use these visuals to corroborate and interpret results.

---

# SPADE：用于抗菌肽发现的智能软件平台

## 1. 项目愿景与动机

SPADE 面向科研人员与产业研发团队，提供可快速检索并能直接用于发现流程的抗菌肽（AMP）数据，把经过整理的条目、清晰的结构与实用的筛选组合在一起，让日常问题无需与格式不一致或来源分散的情况纠缠。

索引覆盖超过 46,000 条肽条目，数据来源交叉引用自 PubMed 与同行评审文献，并整合为统一的模式，在保留出处的同时对关键字段进行标准化，以支持一致、可复现的查询。

数据质量通过兼顾人工判断与自动化处理的流程来维持：记录在多来源间进行交叉核对，当字段存在冲突时由人工整理统一；重复项通过精确序列匹配与规范化名称比对清除，并辅以编辑距离的近重复标记；每次发布都进行分层随机抽样以验证准确性与相关性；我们在索引旁同步给出每次发布的质量指示，包括人工交叉核对计数、自动去重率与抽样覆盖度，让使用者看到数据随时间的维护状态。

为贴合使用习惯，网站支持中文、英文、日文、德文与西班牙文，检索界面采用左侧筛选面板与随条件变化即时更新的结果表；筛选项直接点名用户关心的字段——ID、名称、序列长度、活性类型与目标菌、理化属性（如净电荷、疏水性）以及预测的结构特征——让常见查询一次表达到位。

一个典型的筛选组合可以聚焦对白色念珠菌的抗真菌活性，同时设定净电荷大于 +2 并限定疏水性区间以匹配膜相互作用需求；操作路径保持贴合任务，从检索页设定条件、阅读更新后的结果表，到打开肽卡片查看整合信息，以单页完成细节核查。

## 2. SPADE 平台导览

SPADE 以模块化方式组织页面，贴合常见研究流程。每个页面专注一个任务，导航清晰简洁。

- 首页（home.html）：平台概览和核心模块入口。

![SPADE 首页](source/img/usage/mainpage.jpg "示例图片：主页截图，展示主导航和平台宗旨")

- 智能检索页（search.html）：对超过 46,000 条整理条目进行快速、多维过滤。支持基础属性（ID、名称、长度）、活性类型与目标菌、理化性质（电荷、疏水性）以及结构特征的组合筛选。

![SPADE 检索页](source/img/usage/mainpage.jpg "示例图片：检索页截图，左侧为筛选面板，右侧为结果表")

- 肽卡片页（peptide_card.html）：单条肽信息的整合视图，包含序列、性质、活性、结构及文献来源。

- 可视化页面（amp_visualization.html）：提供疏水性曲线、二维结构预测等图形化视图，便于直观理解。

![肽卡片与可视化](source/img/usage/mainpage.jpg "示例图片：左侧肽卡片，右侧可视化图（如疏水性曲线）")

- 工具页（tools.html）：汇集内部脚本与可信外部工具，支持比对、结构预测、毒性分析等任务。

- 统计页（Statistics.html）：通过交互图表展示全局分布（肽长、活性类型、目标菌等）。

![工具与统计页面](source/img/usage/mainpage.jpg "示例图片：工具页与统计图表示例")

## 3. 设计理念与架构概览

前端为静态网站（HTML/CSS/原生 JavaScript），并在少数处理任务上使用轻量级 Flask 后端。该方案保证界面响应迅速、易于部署，可在普通服务器或 CDN 上稳定运行。

在检索方面，SPADE 使用预编译的 JSON 索引（peptide_index.json），而非关系型数据库。
- 原因：依赖更少、部署更简单、可移植性高，适合缺乏专门 IT 支持的研究团队。
- 取舍：数据库能提供更复杂查询，但同时带来更高复杂度。针对滤器为主的发现任务，单一 JSON + 高效的前端筛选已足够。

页面模块化、耦合度低。新增功能通常只需增加独立页面并接入导航，不影响现有模块。

由于资源成本较高，高级组件（如 RAG 与 Neon 数据库）将按需开放，暂不提供持续的公共访问，以控制滥用与运行成本。

## 4. 使用指南：快速上手

步骤 1：多维检索
1) 在导航栏进入检索页面。
2) 使用左侧筛选面板（基础、活性、结构）设定条件，例如：抗真菌活性、目标为白色念珠菌、净电荷 > +2。
3) 右侧结果实时更新，可根据需要反复调优筛选条件。

步骤 2：分析特定肽
1) 在结果列表中定位感兴趣的肽。
2) 在操作列点击“查看”，进入肽卡片页面。
3) 查看序列、性质、活性、结构与文献来源等信息。

步骤 3：可视化检查
1) 点击“可视化”打开疏水性曲线、二维结构预测等图形视图。
2) 利用图形视图进行辅助判断与结果解释。