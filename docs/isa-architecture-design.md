# ISA 决策助手架构设计

日期：2026-11-17  
项目名称：ISA  
业务定位：基于来源知识提供玩法理解与建议的游戏助手  
当前知识范围：明日方舟—集成战略《黑流树海》

本文描述当前目标架构。仓库目前只有设计文档，没有应用实现、模型安装或领域质量实测；文中的接口和选型是设计约定，不代表已交付能力或已验证事实。数据库结构变更遵循[项目开发规范](../AGENTS.md)，由用户手动执行完整 SQL，不使用自动迁移。

## 目标与边界

当前目标是建设《黑流树海》知识库和有引用的问答闭环。问答根据用户问题检索 active 版本中已审核、版本匹配且来源合格的知识，给出可定位依据、适用条件、风险和未知项。当前通过 Python 开发脚本和测试调用应用用例，不开发交互式 CLI、Web 或桌面界面。

当前范围包括人工整理的 Markdown 资料、原始来源及附件登记、结构化声明与原文证据、知识审核和版本管理、文档切片、混合检索、回答生成、引用校验与完整运行记录。默认检索采用 Dense 与 BM25 召回、RRF 融合和 Cross-Encoder 精排；术语精确命中扩展 BM25 查询，`pg_trgm` fuzzy 可作为独立召回通道。具体配置边界见[技术选型决策](technology-selection.md)。

PySide6 + Qt Quick/QML 是最终桌面方向，当前不实现。截图识别、OCR 拓扑识别、局面状态管理、完整路线搜索、持续读屏和自动资源更新属于后续能力；当前架构不把这些能力描述为已实现的模块或用户流程。RAGFlow、Dify、独立向量库和独立搜索集群不是当前依赖。

## 设计原则

1. 证据先于回答。用于回答的知识能定位到来源、文档版本和具体段落。
2. 版本是硬条件。资料、术语和运行记录保留玩法版本及适用范围。
3. 证据与回答分离。模型只基于符合资格的证据回答；审核、active 选择和引用有效性由确定性流程控制。
4. 先做模块化单体。模块之间有小而稳定的接口，但只有出现真实变化或复用需求时才拆成独立部署单元。
5. 评测驱动调整。检索、排序和模型实现的调整由固定问答案例、证据召回与引用核验结果决定。

## 总体架构

架构按脚本/测试入口、应用层、知识库领域模块、Modular RAG 和基础设施划分。它们位于同一代码库，不按层或模块拆成独立微服务；进程隔离若有需要只解决运行库边界，不改变业务模块所有权。

### 当前入口

开发脚本和测试直接调用应用用例，负责配置组装、提交输入和检查结构化输出。当前没有交互式 CLI、Web 页面或桌面 UI；未来桌面交互通过应用用例访问核心能力，不在界面中实现领域规则。

### 应用层

编排知识维护和问答用例，建立运行上下文，执行固定 Modular RAG 流程，统一处理成功、失败、空证据、未知、取消和记录收尾。评测通过固定样本和测试夹具调用被测用例，不承担知识审核。

### 领域功能模块

- **知识库**：管理知识资料、版本、术语/别名、结构化声明及攻略，提供混合检索和带定位的证据。未经审核的声明不能作为默认回答依据。
- **后续能力边界**：桌面交互、截图/OCR、局面识别、持续读屏、自动资源更新和路线决策不属于当前领域模块。进入开发范围前另行确定需求、数据模型、规则来源和验收标准。

### 基础设施

当前设计涉及数据库/文件存储、Embedding 和生成模型适配。网页自动采集、OCR 与子进程隔离不属于当前实现范围；各适配器只提供技术能力，不决定审核、证据资格或游戏规则。

知识资料由用户提供或人工整理，当前以 Markdown 作为入库文本，图片作为来源原件保存。来源范围和使用许可需要在资料登记时核实。版本策略及默认检索资格按项目讨论文档执行。

## 模块与接口

ISA 采用模块化单体。当前模块边界和后续能力归属如下；此表描述目标设计，不表示代码已经实现。

| 归属 | 模块/内部能力 | 职责与边界 |
|---|---|---|
| 应用层 | knowledge-use-cases | 编排资料导入、知识审核、问答和运行记录；不承载具体检索/生成实现 |
| 应用层 | evaluation | 通过脚本和测试调用用例，检查固定样本与结构化结果；不修改知识审核状态 |
| 知识库 | source/document ingest | 登记来源与附件，解析人工整理的 Markdown，形成待审核内容 |
| 知识库 | catalog/retrieval | 管理版本、声明、术语、审核与证据资格，提供混合召回和证据快照 |
| Modular RAG | orchestration / modules / operators | 按固定三层和六算子流程完成预检索、检索、后处理、生成、引用校验与记录 |
| 基础设施 | 存储 / Embedding / Rerank / 生成模型适配器 | 提供持久化和模型推理能力，不拥有审核或知识规则 |
| 后续能力 | 桌面交互 / 局面 / OCR / 路线决策 | 在单独设计和验收后接入应用用例；当前不作为问答链路前置条件 |

应用用例入口：

- `KnowledgeImporter.import_markdown(source) -> DocumentDraft`：知识维护用例，登记来源和原件，解析 Markdown 并生成待审核文档；发布资格由生命周期、审核状态、版本和来源规则共同决定。
- `QuestionAnswering.answer(question, context) -> AnswerResult`：问答用例，按固定流程检索合格证据、生成回答、校验引用并保存运行记录。
- 桌面、局面和路线用例待相应能力进入开发范围后另行定义。

领域模块接口：

- `Retriever.search(query, context) -> RetrievalResult`：知识库检索接口；context 必含 `scope`、`as_of`、允许的 `evidence_kinds`、active selection/document 清单、词典/索引版本和检索配置快照引用。返回带通道来源、分数及证据快照引用的结果。
- `EvidenceCatalog.select(context) -> EligibleEvidenceSet`：知识库按 `scope + as_of + evidence_kinds`、active selection、审核状态和来源资格固定本次可检索语料。缺少 `as_of`、没有合格 active selection 或请求的 evidence kind 不受支持时显式失败或返回对应未知状态，不扩大候选集合。
- `EmbeddingProvider.embed(texts, space) -> EmbeddingBatch`：指定空间的向量结果，主要供知识库建立索引和查询使用。
- `RerankProvider.rerank(query, candidates, config) -> RerankBatch`：逐项返回输入候选 ID 对应的分数、模型/实现版本和状态；漏项、重复或超长输入按显式契约处理。默认使用 Cross-Encoder。仅在实际配置 `RerankMode=disabled` 时跳过精排，并将模式、原因和事件记入 run。
- `GenerationProvider.generate(request) -> GenerationResult`：按生成契约处理问题和合格证据；引用校验由独立算子负责。

数据库/文件适配器按模块数据归属实现持久化；跨模块读取走显式接口，不通过共享 ORM 对象直接修改其他模块内容。核心契约不依赖 UI、数据库会话或云端 SDK。核心算子统一声明输入/输出、状态、实现版本、配置快照、证据和副作用边界。外部调用失败映射为结构化错误并沿链路传递。

当前不定义 OCR worker、桌面后台任务或局面确认协议。未来引入这些能力时，应另行确定运行时和输入输出契约，并保持核心用例与界面、模型运行库隔离。

## 技术选型

技术路线以[技术选型决策](technology-selection.md)为准。当前采用 Python 3.12 兼容基线、开发脚本和 pytest；不开发交互式 CLI、Web 或桌面界面。最终桌面采用 PySide6 + Qt Quick/QML。以下技术映射描述已确认的目标方案，不表示依赖已安装或实现已验收。
- 数据库：PostgreSQL 16 + pgvector，并启用 `pg_trgm` 做标准术语/别名的辅助模糊匹配。关系数据、版本、审计和向量放在同一数据库。
- 原始文件：本地目录，内容哈希去重；数据库保存路径，不把大文件塞进表中。
- ORM 与结构交付：SQLAlchemy 2.x ORM + psycopg 3；业务读写使用 ORM，向量距离、RRF 融合和批量导入等查询允许使用 SQLAlchemy Core 或绑定参数的原生 SQL。数据库结构变更只更新 ORM/设计并提供完整手工 SQL，由用户执行；禁止自动迁移和应用启动时建表。
- embedding：当前固定使用本地 BGE-M3 dense embedding，列类型为 `vector(1024)`，向量预归一化，距离度量为 cosine distance，索引使用 HNSW 的 `vector_cosine_ops`。云端 embedding 只作为质量/成本比较适配器，不写入当前 canonical embedding 列；需要不同维度时新增独立 embedding space、列和索引，不混用不同维度。
- 生成：通过文本生成 API 能力契约接入；供应商后续锁定。只发送问题所需的合格证据和最小必要上下文。
- 搜索：版本/玩法硬过滤，默认 Dense 与 BM25 召回，可显式加入 fuzzy 通道，RRF 融合后默认由 Cross-Encoder 精排。术语精确命中作为 BM25 查询扩展，不单列通道；具体实现以[技术选型决策](technology-selection.md)为准。

向量索引使用 HNSW 的 `vector_cosine_ops`，构建参数 `m=16`、`ef_construction=64` 归 `embedding_spaces.index_config`；cosine 距离使用 `<=>`，数值越小越接近。每次查询的 `ef_search=max(100, vector_channel_limit)` 归 `retrieval_runs.retrieval_config_snapshot`，当前向量通道上限为 50。索引参数和向量空间定义不能散落在查询代码中。任何近似候选都必须通过 scope/证据资格校验；过滤后不足目标数量时，在同一合法集合上补做精确 cosine 查询并记录实际执行路径。精确查询也是 HNSW 召回评测基线，不允许为补足数量放松过滤条件。当前不选 IVFFlat。

OCR 属于后续能力，当前不选择或部署 OCR 运行时。未来选型需要以目标截图样本验证文字、坐标和拓扑处理能力，并保留人工确认。

RAGFlow 和 Dify 仅作为官方资料核验中的候选工具，不是当前依赖或预定 PoC。

## 中文关键词与术语来源

“关键词”分为可发布词和查询时临时词，来源不同：

1. `terms`/`term_aliases` 是可发布词的主来源，由人工维护并带玩法、版本和审核状态。它包含标准名称、简称、旧称、英文名和来源中明确出现的别名。
2. 网页标题、章节标题、标签和攻略中的显式小标题可以生成候选词，但必须进入待审核状态，不能直接成为规则或别名。
3. 检索查询经过约定的 Unicode、空白和标点归一及术语表映射后，进入 BM25 词法检索与 Dense 向量检索。分词、词典和索引构建按技术选型及实现契约锁定。
4. 术语表可记录简繁映射、同义关系和误识映射；只有经过样本评测确认有效的映射才发布。

因此，中文分词策略由已选 BM25 实现及其词典配置承担；PostgreSQL 原生全文检索和 `pg_trgm` 不替代该词法检索方案。

## 数据模型

本节定义核心实体、关系和字段归属，不是已经部署的数据库 DDL。以下“状态”字段均使用集中枚举；来源捕获信息、内容审核、执行状态和游戏状态分别建模。

### 数据归属

| 责任归属 | 数据 | 边界 |
|---|---|---|
| 知识库 | sources、source_snapshots、documents、active_document_selections、chunks、chunk_embeddings、embedding_spaces、terms、term_aliases、claims | 管理来源、文档版本及其 active 选择、派生索引、术语、声明和审核状态 |
| 应用层与知识库 | retrieval_runs、retrieval_results、retrieval_evidence_snapshots、问答运行记录 | 保存检索上下文、配置、候选、最终证据和完整问答链路 |
| 应用层 | eval_datasets、eval_cases、eval_runs、eval_case_results | 管理固定问答样本、单例结果和聚合指标 |

共用 PostgreSQL 实例不表示共用业务所有权。Embedding 和存储属于基础设施；技术结果由知识库或应用用例解释。

### 枚举与状态契约

共享枚举集中定义在设计路径 `src/isa/contracts/enums.py`，使用 Python 3.12 `StrEnum` 和显式字符串值。该路径是代码组织约定，仓库尚无业务实现。采用 `enums.py`，避免顶层 `enum.py` 与 Python 标准库同名。

| 枚举类 | 当前值域 | 归属 |
|---|---|---|
| `ReviewStatus` | `pending / approved / rejected` | documents、terms、term_aliases、claims 的 `review_status` |
| `DocumentStatus` | `draft / published / superseded` | documents 的文本生命周期 `status` |
| `DocumentKind` | `knowledge` | documents 的用途 `document_kind` |
| `SourceType` | `web / local_file / note` | sources 的 `source_type` |
| `ClaimType` | `fact / rule / strategy` | claims 的 `claim_type` |
| `EvidenceKind` | `claim / guide` | 检索和证据快照的知识类型 |
| `RetrievalChannel` | `dense / bm25 / fuzzy` | retrieval_results 的候选来源通道；术语精确命中作为 BM25 查询扩展，不单独成通道 |
| `RerankMode` | `cross_encoder / disabled` | 检索快照的精排模式；默认 cross_encoder，disabled 仅用于显式实验或配置降级 |
| `RunStatus` | `queued / running / succeeded / failed / cancelled` | 问答、检索和评测运行的执行状态 |
| `EmbeddingSpaceStatus` | `building / active / retired` | embedding_spaces 的 `status` |
| `DatasetStatus` | `draft / frozen / retired` | eval_datasets 的 `status` |
| `EvalCaseKind` | `retrieval / answer` | eval_cases 的 `case_kind` |
| `EvalVerdict` | `pass / fail / not_scored` | eval_case_results 的 `verdict` |

导入是一个动作，不是审核结果。解析完整且 scope 明确的知识文档可发布为 `status=published, review_status=pending`；解析未完成、scope 未确认或尚未发布的文档为 `draft`。审核结果只能取 ReviewStatus；`approved` 不代表自动选中，`superseded` 文档仍退出当前检索。

审核采用 `pending → approved/rejected`；内容修正生成新版本并回到 `pending`，不覆盖已被运行记录引用的内容。固定评测运行仅使用 frozen 数据集。所有运行使用 RunStatus，终态后重试另建 run。

ORM 与外部结构校验复用同一枚举定义；数据库使用文本列与具名 CHECK 约束，所有结构变更由用户手动执行 SQL，不自动迁移或建表。contracts 模块只依赖标准库，不导入 UI、ORM 或模型运行库。

### 来源与知识资料

- `sources`：逻辑来源，例如一个 canonical URL、一份用户上传资料或个人笔记；保存 `source_type: SourceType`、canonical URI 和许可备注，不保存某一次抓取的内容。不同用户上传不会因共用上传入口而成为同一个逻辑来源。
- `source_snapshots`：来源的不可变字节快照；保存 `source_id`、捕获 URI、抓取/上传时间、MIME、原始路径、`content_sha256`、大小和来源地区/版本提示。相同 URL 的不同抓取各有一行；相同字节按哈希复用物理文件，不合并捕获记录。快照内容不随解析或审核更新。
- `documents`：从 `source_snapshots` 经过指定解析管线生成的文本版本；保存解析版本、规范化全文哈希、scope、`document_kind: knowledge`、生命周期、审核状态及被替代版本。旧版本保留；默认回答只选择 active 版本中已审核且来源合格的资料。
- `active_document_selections`：保存用户对某一 `source_id + Scope` 当前选择的 `document_id`、选择时间和操作者。每个 source/scope 仅一条当前选择；切换只更新选择，不覆盖旧 document。所选文档必须属于该 source/scope、已发布且审核通过。`approved` 只表示审核通过，不代表 active；运行封存选择记录 ID 和 document 版本清单，因此之后切换不会改变历史运行。
- `chunks`：某个 document 的不可变文本片段、章节、页码/坐标、规范化文本、序号、`chunker_version`、`chunk_content_sha256` 和解析置信度；置信度可为 null。`chunk_id` 标识片段实例；内容哈希只用于内容去重、缓存和快照校验，不能替代片段实例主键。
- `chunk_embeddings`：chunk_id、space_key、向量、归一化信息和创建时间；维度、模型 revision 与距离度量通过 embedding_spaces 关联。不同向量空间不混用。
- `embedding_spaces`：空间标识、模型 revision、预处理版本、维度、距离度量、归一化方式和索引配置。切换模型需使用独立空间并在评测后发布。
- `terms` / `term_aliases`：标准术语、别名、分类、不可变 revision、完整 scope/适用时间、来源引用和 review_status；运行保存选定词典 revision，新增别名不改变旧运行。
- `claims`：经版本管理的事实、规则描述或攻略策略，关联证据 chunk，带 `claim_type: ClaimType`、`review_status: ReviewStatus`、来源权威度说明、置信度和完整 scope。规则知识使用 `claim_type=rule` 表达；当前问答只解释来源内容，不执行状态转移。

原始来源快照、规范化文档和片段分别记录内容哈希，用于原件去重、解析版本识别、缓存和检索快照校验。内容哈希不替代来源、文档或片段实例标识。

### 问答与审核

- 问答运行记录保存问题、规范化问题、active 版本及选择依据、算子配置、生成请求/响应、回答、引用校验、状态和错误，并关联检索运行及证据快照。具体表名和字段由 ORM/手工 SQL 任务确定。
- `review_annotations` 关联知识对象及版本，保存审核决定、来源定位和修正结果。内容修正生成新版本，不覆盖被历史运行引用的内容。

### 检索和评测记录

- `retrieval_runs`：query 原文/规范化文本、玩法范围、必填 `as_of`、非空允许的 `evidence_kinds`、active selection ID 及实际 document/claim 版本清单、查询 embedding 及空间版本、`retrieval_config_snapshot`、`RunStatus` 和时间。快照记录 BM25 词典/统计版本、Dense/Fuzzy 参数、向量查询参数、实际启用通道、执行路径、RRF 及 `RerankMode`/精排配置。重算创建新 run。
- `retrieval_results`：`retrieval_run_id`、`chunk_id`、可空 `claim_id`、实际 `evidence_kind`、候选来源 `RetrievalChannel`、内容哈希、各通道名次/原始分数、RRF 与精排分数、最终名次及是否进入证据包。候选保留来源定位。
- `retrieval_evidence_snapshots`：关联 `retrieval_result_id`，保存入选文本、claim 内容、来源 URI/捕获时间/原件哈希、页码/坐标、scope、`as_of`、审核状态、实际 `evidence_kind` 和序列化版本；解释模型引用这里的不可变证据 ID。
- `eval_datasets`：名称、不可变数据集 revision/哈希、scope、schema 版本、构建说明和 `status: DatasetStatus`。
- `eval_cases`：dataset revision、`case_kind: EvalCaseKind`、问题输入、标注快照、期望证据和判定依据。
- `eval_runs`：固定 dataset revision、指标版本/阈值、代码版本、关联运行 ID、`RunStatus`、起止时间和聚合指标。
- `eval_case_results`：`eval_run_id/case_id`、关联检索/问答 run ID、单例指标、时延、资源占用、`verdict: EvalVerdict`、人工判定、错误和输出快照；失败样本不能从分母中静默删除。

所有执行记录和选中内容在完成后封存；内容纠错生成新版本，旧运行所引用的版本不覆盖或物理删除。运行配置先从部署默认值解析，再将实际值封存到所属运行记录。

`Scope` 由 `region/game_version/mode_revision/mode` 四个相等匹配字段组成；`effective_from/effective_to` 是该 scope 内知识内容的适用时间区间，采用 UTC 的 `[from,to)`，可空边界表示单侧无界，不表示跨版本通用。每次检索运行必须保存请求的 `as_of`，与 `captured_at`、发布日期及 active 选择分别使用，并以 `effective_from <= as_of < effective_to`（空边界视为无界）筛选。`as_of` 不回溯推导 active 选择；run 固定请求开始时取得的用户选择快照。版本未知资料保持 draft，不能通过 null 或“最新”标签绕过过滤；部署配置必须绑定具体地区和版本值，当前尚无资料可核定这些值。

字段归属如下：`documents`、`terms`、`term_aliases`、`claims` 各自保存完整 scope 和适用时间区间；`active_document_selections` 以 source/scope 选择 document 版本；`chunks/chunk_embeddings` 通过 documents 继承。active 选择不替代文档审核。关联 claim 和来源 document 的适用区间必须覆盖本次查询时间。问答运行和证据快照封存实际使用值；sources/source_snapshots 保存捕获信息，不承担检索资格。

### 运行配置归属

| 配置 | 定义/默认值 | 本次运行的规范记录 |
|---|---|---|
| 解释器、设备、模型缓存、超时 | 部署 runtime 配置 | 运行记录中的 runtime 配置标识；不写机器路径到 embedding space |
| 模型 revision、维度、归一化、索引构建参数 | embedding_spaces | chunk_embeddings 关联 space；检索记录所用 space revision |
| Dense/BM25/fuzzy 通道、RRF 与 rerank 参数 | 检索默认配置及显式实验/降级覆盖 | retrieval_runs.retrieval_config_snapshot；记录实际通道、`RerankMode` 和事件 |
| 生成模型、提示模板、发送证据及响应 | 问答请求 | 问答运行记录的生成请求/响应快照 |
| 数据集、指标定义和验收阈值 | 冻结评测集和指标配置 | eval_runs；通过关联运行读取检索配置 |

问答运行通过外键关联检索记录，不保存一份会与检索记录分歧的重复配置副本。

## 业务流程与知识检索

### 知识库维护流程

1. 通过知识导入用例登记来源和原件快照；当前入库文本为用户提供的人工整理 Markdown。
2. 知识库解释提取结果，规范化术语、scope 和适用时间，生成 knowledge 文档草稿；人工修正不覆盖原件或已封存版本。
3. 按来源、版本和玩法生成 chunk；构建 BM25 词法索引，并调用 EmbeddingProvider 生成归一化 1024 维 BGE-M3 向量写入 `chunk_embeddings`。两路索引必须关联同一份语料清单。
4. 按文档生命周期和审核契约发布资料、术语、claim 和规则。维护完成的内容可供后续问答检索。

### 问答流程

1. 请求入口锁定玩法范围、`as_of`、允许的 `evidence_kinds`、active selection/document 清单和算子配置快照。`as_of` 过滤适用时间；active 选择是请求时用户设定，两者不互相推导。
2. QueryPrecheckOperator 校验问题与范围并执行术语归一及精确词条扩展；HybridRetrieveOperator 以 Dense 与 BM25 召回，并可按显式配置加入 `fuzzy` 通道，再通过 RRF 融合。
3. EvidenceFilterOperator 复核审核、版本和来源资格，默认使用 Cross-Encoder 精排并组织证据上下文。仅显式 `RerankMode=disabled` 时跳过精排，并记录原因及事件。
4. AnswerGenerateOperator 基于证据生成回答；CitationValidateOperator 检查引用结构、证据 ID、发送内容及来源定位。
5. RecordOperator 保存完整链路。空证据、资料不足、版本不匹配、引用失败和算子错误保持独立可识别状态；重算创建新运行。

### 知识库证据类型与过滤口径

证据使用同一 Scope/as_of 定义，但资格和用途分开：

| evidence_kind | 来源资格 | 允许用途 |
|---|---|---|
| `claim` | active 版本中已审核、版本匹配且来源合格的结构化声明 | 作为有来源的知识事实或机制回答 |
| `guide` | active 版本中已审核、版本匹配且来源合格的攻略资料 | 归纳攻略思路并解释适用条件；不能单独认定游戏规则 |

默认检索排除 draft/superseded、pending、rejected 和 scope 未确认资料。攻略文本用于有来源的归纳，不因模型生成而升级为已审核游戏事实。

规则类声明仅作为有来源的知识内容参与问答；当前不将其解释为可执行的局内规则。

### 知识库混合检索与融合

1. 运行清单快照保存 `scope`、`as_of`、`evidence_kinds`、active selection ID、文档/claim、词典和向量空间版本。active 选择由用户显式设置；`as_of` 仅匹配适用时间。所有通道在同一合格语料内执行，不能临时重选最新文档。
2. HybridRetrieveOperator 分别执行 Dense 与 BM25 召回，并按配置加入 fuzzy 独立通道；保留候选名次、分数和通道状态，术语精确命中仅作为 BM25 查询扩展，再用 RRF 合并候选。实际参数、启用通道和索引清单封存到 `retrieval_config_snapshot`。
3. EvidenceFilterOperator 再次校验证据资格，默认使用 Cross-Encoder 精排并组织证据上下文。`RerankMode=disabled` 必须显式配置；精排调用失败按结构化错误处理，不静默绕过。
4. 按固定预算选择完整证据，封存实际发送的证据 ID、文本、来源定位、适用条件和版本，并向应用层返回证据快照引用。

## 后续能力边界

未来若进入桌面交互、截图/OCR、局面识别或路线决策范围，应单独确认用户流程、输入模型、规则来源、数据所有权及验收标准，并与当前知识问答链路保持明确接口。当前架构不定义这些能力的数据表、状态转移、搜索算法或界面协议。

## 验收与评测

当前验收围绕知识维护与有引用问答闭环，检验资料资格、检索、回答、引用和运行记录。评测由脚本和测试调用应用用例；固定样本、gold 证据、指标及判定阈值在相应评测设计中确定，并随评测运行封存。当前没有已确认的数值阈值或已测质量结果。

评测覆盖版本、审核与来源过滤，标准术语和别名，BM25/Dense 召回与排序，引用定位及支持度，以及历史运行回放。指标用于技术验收和质量测量，不替代人工审核或游戏规则确认。

## 风险与处理

- 版本混淆：资料按 scope 和 as_of 过滤，非当前版本请求明确拒绝；存在来源冲突的内容在审核前不进入默认回答上下文。
- 专有名词召回失败：知识库维护术语/别名表，通过固定样本评测精确、词法和向量检索表现。
- 来源许可：资料使用范围需在登记时核实，不绕过登录、访问控制或明确的采集限制。
- 模型幻觉：模型只接受合格证据包；没有足够证据时返回未知或要求补充，不生成未经来源支持的事实。
- 数据增长与备份：数据库、原件、运行快照与模型/配置清单一并备份；embedding 和检索索引是可重建派生物，但重建不是历史回放的替代，不能删除仍被运行引用的版本。
- 来源许可：资料登记时检查来源条款和许可，并保存出处。

## 关联文档

- [项目结构与骨架搭建指南](project-structure.md)：目录职责、单向依赖、契约唯一来源与最终桌面 MVVM 接入规划。
- [项目讨论与开发决策](project-discussion.md)：产品范围、知识规则和 Modular RAG 固定边界。
- [技术选型决策](technology-selection.md)：已选技术、未选理由和验证状态。
- [官方资料核验](official-sources.md)：工具事实、许可证及其与当前范围的关系。
- [Modular RAG 工具角色核验](research-rag-tools.md)：框架能力比较和适配边界。
