# ISA 项目结构与骨架搭建指南

日期：2026-11-19  
状态：目标结构与搭建约束；仓库尚无业务实现。  
范围：当前知识库与有引用问答闭环，以及最终桌面 MVVM 的接入规划。

## 1. 应用需求

### 1.1 初期目标

围绕《明日方舟》集成战略「黑流树海」，建设人工 Markdown 资料导入、原件保存、结构化声明、版本与审核、切片与索引、混合检索、回答生成、引用校验和完整运行记录。通过开发脚本与测试调用用例，不开发交互式 CLI、Web 或桌面。

默认回答仅使用 active、审核通过、范围与适用时间匹配且来源合格的资料。内容追加保存，历史运行固定当时的输入、证据、版本与配置。active 选择由用户手动设置，审核通过不自动激活。

### 1.2 最终目标

最终采用 PySide6 + Qt Quick/QML 桌面应用，接入画面识别、局内状态更新和决策建议。桌面表现层采用 MVVM，复用应用用例和知识能力。持续读屏、OCR 拓扑识别、完整路线搜索和 Agent 均属于后续独立设计范围，不能成为当前问答链的前置依赖。

### 1.3 文档权威与适用边界

- [项目讨论与开发决策](project-discussion.md)定义产品目标、知识规则与能力范围。
- [技术选型决策](technology-selection.md)定义技术路线、类型化状态和调度语义。
- [总体架构设计](isa-architecture-design.md)定义总体模块、数据归属和领域模型。
- 本文定义目录、静态依赖、公共入口、契约归属与骨架验收，不重复定义枚举值域和完整字段。
- [开发规范](../AGENTS.md)规定 SOLID、数据库操作和任务交付要求。

下文的文件树是目标设计，不代表能力已交付。骨架按实际任务逐步建立，不批量创建没有职责实现的空目录。

## 2. 用户场景与输入输出

| 场景 | 输入 | 输出与边界 |
|---|---|---|
| 维护知识 | 原件、人工 Markdown、来源、范围和声明 | 待审核版本及导入结果；不自动设置 active |
| 构建索引 | 指定文档版本、切片和模型配置 | 一致的片段、向量、词法索引与构建清单 |
| 问答 | 问题、Scope、as_of、允许的 evidence_kinds | 建议、机制、前提、风险、未知、引用及执行和记录结果 |
| 历史回放 | run_id | 当时封存的输入、证据和输出；重新计算另建运行 |
| 评测 | 冻结题集、gold、指标配置 | 单例和聚合结果；不修改知识审核结论 |
| 桌面交互（后续） | 用户操作、应用结果 | QML 界面状态；业务规则仍由核心拥有 |

## 3. 相关技术

整体采用**模块化单体 + 六边形架构（端口与适配器）**；RAG 内部采用**固定三层流水线**；最终桌面表现层采用 **MVVM**。

| 模式 | 解决的问题 | 在 ISA 中的落点 |
|---|---|---|
| 模块化单体 | 保持业务模块分离，控制部署与运维成本 | 同一代码库中的 application、knowledge、rag；当前不拆微服务 |
| 六边形架构 | 让用例和规则独立于外部技术 | 核心消费 ports，基础设施实现 ports，bootstrap 注入实现 |
| 三层流水线 | 明确 RAG 调度、能力阶段和最小替换单元 | orchestration → modules → operators |
| MVVM | 分离界面展示、交互状态与业务能力 | QML View → Python ViewModel → 应用用例 |

Python、标准库契约、TOML、pytest、SQLAlchemy 与模型适配等技术遵循技术选型文档。本文不新增依赖或锁定未经验证的库版本。

## 4. 方案与架构

### 4.1 当前目标目录

树中省略 Python 包的 `__init__.py`。目录用于表达职责；小规模实现可以先用一个文件承载一项职责，增长后再按同一归属拆分。

```text
ISA/
├─ pyproject.toml                    # 包元数据、依赖分组、质量工具配置
├─ uv.lock                           # 当前环境的依赖锁定结果
├─ README.md                         # 项目介绍、准备方式和开发入口
├─ AGENTS.md                         # 开发约束
├─ docs/                             # 产品、架构、技术与任务文档
│  ├─ project-discussion.md           # 目标、知识规则和产品边界
│  ├─ technology-selection.md         # 技术决策与验证状态
│  ├─ isa-architecture-design.md      # 总体模块与数据归属
│  ├─ project-structure.md            # 本文：目录、依赖和搭建验收
│  └─ tasks/                         # 每项能力的设计、实现和验收记录
├─ config/                           # 可版本化的部署默认值，不放密钥
│  ├─ application.toml               # 环境、路径、超时等运行默认值
│  ├─ retrieval.toml                 # 通道、RRF、精排等检索默认值
│  └─ generation.toml                # 生成模型和请求默认值
├─ scripts/                          # 非交互开发入口，只做组装、调用与输出
│  ├─ import_markdown.py             # 调用知识导入用例
│  ├─ ask_question.py                # 调用问答用例
│  ├─ replay_run.py                  # 调用封存结果回放用例
│  └─ evaluate.py                    # 调用固定题集评测用例
├─ src/isa/
│  ├─ contracts/                     # 唯一公共契约来源，仅依赖标准库
│  │  ├─ enums.py                    # 显式枚举，不使用顶层 enum.py
│  │  ├─ scope.py                    # Scope、适用时间等公共值类型
│  │  ├─ evidence.py                 # 来源定位、证据和不可变快照引用
│  │  ├─ errors.py                   # 结构化错误与因果信息
│  │  ├─ knowledge.py                # 知识维护输入输出与文档、声明契约
│  │  ├─ retrieval.py                # 检索请求、候选、语料清单与配置快照
│  │  ├─ answer.py                   # 问答输入输出、生成与引用校验契约
│  │  ├─ execution.py                # 运行上下文、算子结果、状态与步骤记录
│  │  ├─ evaluation.py               # 数据集、评测输入输出和指标结果
│  │  └─ ports/                      # 核心消费的技术能力接口
│  │     ├─ storage.py               # 按用途分离的知识、文件和运行存储接口
│  │     ├─ parsing.py               # 文档解析能力接口
│  │     ├─ retrieval.py             # 候选查询与向量、词法索引能力接口
│  │     └─ models.py                # Embedding、Rerank、Generation 接口
│  ├─ application/                   # 用户操作级用例与跨能力协调
│  │  ├─ knowledge.py                # 导入、审核等知识维护用例
│  │  ├─ indexing.py                 # 索引构建、检查和发布用例
│  │  ├─ question_answering.py        # 问答入口，调用 RAG 编排
│  │  ├─ replay.py                    # 读取历史封存结果
│  │  └─ evaluation.py               # 固定题集运行、指标计算与结果封存
│  ├─ knowledge/                     # 知识业务与检索能力，不依赖 RAG
│  │  ├─ api.py                      # 对外唯一公开入口，显式导出稳定能力
│  │  ├─ domain/                     # 版本、审核、来源和资格等业务规则
│  │  ├─ ingestion/                  # 解析结果整理、声明校验与草稿形成
│  │  ├─ chunking/                   # 导入切片算子：结构优先、超长递归
│  │  ├─ indexing/                   # 派生数据、索引清单与就绪一致性
│  │  ├─ catalog/                    # active 选择读取、合格语料固定与复核
│  │  └─ retrieval/                  # 术语扩展、通道组合、RRF 与证据选择
│  ├─ rag/                           # 问答流水线，保留固定三层
│  │  ├─ orchestration/              # 编排层：唯一调度权威
│  │  │  ├─ scheduler.py             # 状态转换、结果接纳与统一收尾
│  │  │  ├─ plan.py                  # 固定计划、模块和算子顺序
│  │  │  └─ policies.py              # 有限重试、取消与显式降级策略
│  │  ├─ modules/                    # 模块层：阶段输入输出衔接
│  │  │  ├─ pre_retrieval.py         # 预检索
│  │  │  ├─ retrieval.py             # 检索
│  │  │  ├─ post_processing.py       # 后处理
│  │  │  ├─ generation.py            # 生成与引用校验
│  │  │  └─ recording.py             # 横切收尾入口，不新增检索业务阶段
│  │  └─ operators/                 # 算子层：最小可替换执行单元
│  │     ├─ query_precheck.py        # QueryPrecheckOperator
│  │     ├─ hybrid_retrieve.py       # HybridRetrieveOperator
│  │     ├─ evidence_filter.py       # EvidenceFilterOperator
│  │     ├─ answer_generate.py       # AnswerGenerateOperator
│  │     ├─ citation_validate.py     # CitationValidateOperator
│  │     └─ record.py                # RecordOperator
│  ├─ infrastructure/               # 技术适配器，实现 contracts/ports
│  │  ├─ postgres/                  # PostgreSQL 连接与数据访问实现
│  │  │  ├─ models/                 # 按知识、运行、评测所有权分组的 ORM
│  │  │  ├─ repositories/           # 对应小存储接口的实现
│  │  │  └─ queries/                # pgvector、pg_trgm 等专用查询
│  │  ├─ filesystem/                # 原件、哈希、快照及索引文件存取
│  │  ├─ parsing/                   # markdown-it-py 等解析适配
│  │  ├─ lexical/                   # BM25 分词、构建与查询适配
│  │  ├─ models/                    # 模型技术实现
│  │  │  ├─ embedding/              # BGE-M3 适配
│  │  │  ├─ rerank/                 # Cross-Encoder 适配
│  │  │  └─ generation/             # 生成供应商 API 适配
│  │  └─ diagnostics/               # 关联 ID、脱敏与诊断日志
│  └─ bootstrap/                    # 唯一具体依赖组装位置
│     ├─ settings.py                # TOML、环境变量读取与配置边界校验
│     └─ container.py               # 构造适配器并注入核心，提供用例
├─ tests/                           # 自动验证，与生产实现分离
│  ├─ architecture/                 # 导入方向、公共入口与契约隔离
│  ├─ contracts/                    # 算子和适配器的可替换性验证
│  ├─ unit/                         # 业务规则、状态转换和纯算法
│  ├─ integration/                  # 外部技术适配及组合验证
│  ├─ acceptance/                   # 用例闭环与失败收尾验证
│  └─ fixtures/                     # 最小资料、假实现与固定输入
├─ evaluation/                      # 版本化评测资产，不放业务实现
│  ├─ datasets/                     # 冻结题集、gold 和人工标注
│  └─ metrics/                      # 指标定义说明与配置
└─ sql/
   └─ manual/                       # 与最终 ORM 一致的完整手工 SQL
```

运行数据位于配置指定的外部数据根目录，包括原件、封存快照、派生索引、模型缓存和临时文件。源码仓库仅保留必要的小型测试与评测资产，不提交密钥、个人配置、大模型权重或真实运行数据。临时文件与被历史引用的不可变资料采用不同的保留规则，不能将后者当缓存清理。

### 4.2 单向静态依赖

下列箭头表示“允许导入或引用的方向”，不表示返回值流向，也不表示每个文件必须导入所有列出的包。未列出的跨包依赖不默认放行。

| 调用方 | 允许依赖 | 禁止依赖 |
|---|---|---|
| scripts | bootstrap、application、contracts | knowledge 内部、RAG 内部、具体技术适配器 |
| bootstrap | application、rag、knowledge、infrastructure、contracts 的明确构造入口 | scripts、presentation |
| application | rag.orchestration、knowledge.api、contracts | infrastructure、bootstrap、Qt、ORM、供应商 SDK |
| rag.orchestration | rag.modules、contracts | rag.operators、knowledge 内部、infrastructure |
| rag.modules | rag.operators、contracts | orchestration、application、infrastructure |
| rag.operators | knowledge.api、contracts | modules、orchestration、application、infrastructure |
| knowledge.api | knowledge 内部实现、contracts | rag、application、infrastructure、bootstrap |
| knowledge 内部实现 | knowledge.domain、contracts | 其他业务模块与具体技术适配器 |
| knowledge.domain | contracts | knowledge 其他目录、ORM、模型运行库 |
| infrastructure | contracts、第三方技术库；其内部按下述规则组织 | application、rag、knowledge 实现、bootstrap |
| contracts.ports | contracts 中相应数据类型、标准库 | 核心实现、其他端口的具体实现、第三方库 |
| contracts 数据类型 | 无环引用的其他契约数据类型、标准库 | ports、任何实现模块、第三方库 |

补充规则：

1. `knowledge.api` 显式导出公开能力，不用通配导入或导出所有内部对象。跨知识库调用只使用此入口，不建立多份转发接口。
2. 知识库同级功能目录不互相深层导入；跨功能协作由公开能力的实现协调。可复用规则下沉 `domain`，不通过循环调用共享。
3. `knowledge.api`、RAG 模块入口和算子构造入口由 bootstrap 显式组装；核心运行时不得反查 container 或全局注册表。
4. 基础设施内部允许 repository/query 依赖 ORM 映射和连接设施，模型、解析等适配器保持独立；需要组合不同适配器时由 bootstrap 注入端口。内部也不得形成循环依赖。
5. `__init__.py` 保持轻量，不通过重导出间接加载数据库连接、模型或 Qt。`TYPE_CHECKING` 内的导入也必须满足所有权与依赖方向。
6. 内部相互依赖需细化为无环关系；目录级规则不能作为包内任意互调的许可。架构检查同时覆盖包内循环。

核心关系可简写为：

```text
开发入口 → 应用用例 → RAG 编排 → 阶段模块 → 算子 → 知识公开能力
                     核心各层 → contracts ← 技术适配器
                                     ↑
                   bootstrap 构造实现并注入相应端口
```

### 4.3 职责分离

| 位置 | 负责 | 不负责 |
|---|---|---|
| application | 用户操作、跨能力协调、调用编排 | 检索算法、SQL、供应商消息拼装 |
| knowledge | 知识版本、审核、资格、检索与证据选择 | 调度问答主链、生成建议、管理界面 |
| orchestration | 固定路由、状态转换、重试、取消、终结 | 理解 SQL、模型 token 或重写检索算法 |
| modules | 表达阶段、组织本阶段算子输入输出 | 第二套调度状态机、跨阶段自行跳转 |
| operators | 校验步骤契约、调用能力、返回结果和追踪 | 修改全局 ChainState、决定任意下一步 |
| infrastructure | 持久化、文件、解析和模型技术调用 | 审核结论、active 选择策略、游戏规则 |
| bootstrap | 配置解析、对象构造、依赖注入、资源生命周期 | 业务分支与问答处理逻辑 |

`HybridRetrieveOperator` 调用知识库混合检索能力；术语扩展、通道组合与 RRF 只在知识库实现一次。Dense、BM25、fuzzy、融合都保留具名子步骤和事件。

`EvidenceFilterOperator` 调用知识库资格复核与证据选择能力，并按配置使用注入的 RerankProvider。资格规则来自同一领域实现，入口筛选与后置复核不复制规则。知识库负责候选选择策略，模型适配器只返回按候选 ID 对齐的精排技术结果。

切片是导入链路能力，不进入问答六算子主链。`recording` 是横切收尾模块，不增加第五种检索业务阶段或第七个顶层算子。

### 4.4 最终桌面采用 MVVM

整体架构与 MVVM 作用层面不同：模块化单体和六边形架构组织整个应用，MVVM 组织桌面表现层。初期无界面，不引入 Qt 或 ViewModel。

```text
src/isa/
├─ presentation/
│  └─ desktop/
│     ├─ qml/                      # View：布局、展示、动画和用户操作转发
│     ├─ viewmodels/               # ViewModel：可绑定状态、命令和结果映射
│     ├─ execution/                # 后台任务、取消及 GUI 线程结果交付
│     └─ resources/                # 图标、字体和 QML 资源
├─ perception/                     # 后续：识别结果解释与候选观测
├─ session/                        # 后续：局内状态、更新和确认规则
├─ routing/                        # 后续：审核规则支持的确定性路线能力
└─ infrastructure/
   ├─ capture/                     # 后续：截屏技术适配
   ├─ ocr/                         # 后续：OCR 运行库适配
   └─ workers/                     # 后续：确有兼容性需要时的进程适配
```

这些路径仅表示未来职责位置。进入相应开发任务后再确认数据、协议和验收标准，不提前建立空包或承诺进程划分。

| MVVM 角色 | 目录对应 | 允许的行为 |
|---|---|---|
| View | presentation/desktop/qml | 绑定属性、显示结果、转发用户操作；仅保留展示逻辑 |
| ViewModel | presentation/desktop/viewmodels | 用 Qt 属性和信号暴露界面状态，通过注入用例执行操作并映射结果 |
| Model | application、knowledge、rag 等核心能力 | 执行业务、确定资格、生成与校验答案；不依赖 Qt |

Model 表示界面背后的业务能力，不等于 PostgreSQL ORM 模型。ViewModel 的加载、选中、展示错误等界面状态与核心 ChainState 分开，不能产生第二套业务执行真相。

桌面依赖方向：`QML View → ViewModel → application/contracts`。ViewModel 可使用注入的 execution 执行设施；execution 仅承接任务执行、取消和线程交付，不承担业务策略。Python 表现层不得导入 knowledge 内部、RAG 内部或 infrastructure。bootstrap 注入应用用例和执行设施，桌面入口负责启动 QML；bootstrap 不导入表现层。

同步核心用例可由桌面后台执行设施调用。结果经 GUI 线程更新 Qt 属性，长任务不阻塞界面；取消语义沿核心契约传递，不将界面取消按钮等同远端调用已经停止。界面对象、Qt 信号和线程句柄不得进入核心契约。

感知、局内状态、路线与知识能力之间的业务协作由应用用例组织，通过标准库契约交换结果；不引入同级模块互相导入。未来 Agent 只能作为受限算子，通过明确的底层能力端口访问 RAG 能力，不反向导入顶层 scheduler，不更改审核或 active。

## 5. 数据模型与接口

### 5.1 契约的唯一来源

| 对象 | 唯一来源 | 约束 |
|---|---|---|
| 枚举、Scope、时间区间 | contracts/enums.py、scope.py | ORM、校验和核心复用；不复制值域 |
| 请求、结果、证据、快照引用 | contracts 对应数据文件 | 跨模块使用同一类型，不各自创建同名 DTO |
| 运行上下文、算子结果、记录回执 | contracts/execution.py | 不持有 Qt、数据库会话或框架 State |
| 技术能力接口 | contracts/ports | 按消费者用途分离，每个 Protocol 只声明必要能力 |
| 知识规则 | knowledge/domain | 不在算子、UI 和 repository 重复实现 |
| ORM | infrastructure/postgres/models | 仅描述持久化映射，不能跨基础设施返回实例 |
| 供应商消息与外部校验结构 | 适配器或输入边界内部 | 映射公共契约，不另建权威业务定义 |

契约唯一不等于所有对象放在单一大文件，也不等于一个全能接口。按知识读取、资料保存、运行记录、文件存取等实际用途隔离 ports。公共契约只纳入实际跨模块交换的内容，内部临时对象保留在拥有它的实现中。

公共数据类型与能力端口各定义一次。`knowledge.api` 是业务能力公开入口，`contracts/ports` 是核心消费的外部技术接口，两者不能为同一职责各自维护一份冲突签名。内部标准库数据结构与外部 Pydantic 校验模型可分别存在，但使用相同枚举和规则，映射由输入边界负责。

### 5.2 算子、运行与记录

固定顶层顺序：

```text
QueryPrecheckOperator → HybridRetrieveOperator → EvidenceFilterOperator
→ AnswerGenerateOperator → CitationValidateOperator → RecordOperator
```

每个核心算子声明输入、输出、状态、实现版本、实际配置快照、证据和副作用边界。算子只返回 OperatorResult，ChainState 仅由 scheduler 受控更新。状态值域和转换复用技术选型文档，不在本文另造枚举。

前序失败、空证据、资料不足、版本不匹配或取消时，停止依赖其结果的业务步骤，记录跳过原因并统一收尾。引用失败不得作为已验证回答交付。错误保留类型、来源算子、消息、详情、retryable 和链路位置；有限重试与显式降级由调度策略控制，原始失败不被覆盖。

RecordOperator 独立保存完整规范链路，诊断 logging 不能替代它。记录至少包含关联 ID、时间与环境、问题、版本选择依据、流程与算子顺序、每个尝试的契约和配置、召回候选、最终证据及来源、生成请求响应、模型、引用检查、错误、未知、降级、重试、耗时、指标和回放哈希。具体字段以技术选型及总体架构为准。

执行进度、业务结果、记录结果分别表达。只有业务成功且记录成功才报告整体成功；记录失败保留原业务结果和独立错误，不递归调用 RecordOperator。自身的版本、配置、尝试与写入结果通过提交元数据和回执关联，不承诺异常进程终止时可靠收尾。

### 5.3 版本、配置与数据所有权

- Scope 使用 region、game_version、mode_revision、mode 四字段；as_of 只过滤适用时间，不推导 active。
- 每个请求固定 active selection、文档/声明、词典、索引、模型与实际配置；不随运行期间的 active 切换变化。
- approved 不等于 active；draft、未审核、范围不明或来源不合格内容不得进入默认回答上下文。
- 所有检索通道使用同一合格语料清单；精确补查不得放宽版本、审核或来源过滤。
- 配置文件是部署默认值；规范记录保存本次实际解析配置。检索配置只由检索运行拥有，问答通过引用关联，不维护分歧副本。
- 知识、运行和评测在同一数据库内仍有独立所有权。持久化接口不授予调用方修改其他模块数据的能力。
- 文件与数据库不是同一原子事务；适配器实现需定义暂存、原子改名、引用提交和失败恢复。不用 repository 内部自动重试掩盖副作用失败。

## 6. 实现步骤

以下按能力依赖指导骨架搭建，不表示对应能力已经实现。

1. **建立最小可验证包。** 创建 pyproject、src 布局、tests 和必要配置。接入 Ruff、mypy、pytest；导入核心包不创建连接、不加载模型、不执行数据库操作。
2. **确定契约与边界。** 实现当前需要的数据类型和小端口，先固定状态、错误、证据和运行配置语义。建立静态依赖检查，防止后续接入适配器时反向依赖。
3. **打通假实现链路。** 用测试假算子、假提供方和内存记录实现验证三层六算子、跳过、失败、取消及统一收尾。假证据明确为测试夹具，不能当真实知识验收。
4. **建立知识能力。** 接入 Markdown、原件、领域规则、审核与版本契约。涉及数据库结构时仅交付 ORM 和完整手工 SQL，明确提示“请手动在 PostgreSQL 执行”；不创建自动执行入口。
5. **接入索引与检索适配。** 在同一语料清单下验证切片、Dense、BM25、可选 fuzzy、RRF 和 Cross-Encoder。默认精排不静默跳过，实验或降级必须显式配置和记录。
6. **完成真实问答与评测。** 接入生成 API、独立引用检查、规范记录和回放，用固定样本验证；模型与供应商版本在任务中锁定，不编造质量结论。
7. **按需建设桌面 MVVM。** 在核心用例稳定、桌面任务进入范围后创建 presentation，先验证属性绑定、后台调用、取消和结果交付，再逐项接入识别、局内状态与路线能力。

每项实际实现任务使用项目统一 Markdown 模板记录需求、设计、实现、验收及未解决项；本文是骨架设计任务的交付文档，不替代后续能力任务的验收记录。

## 7. 验收标准

### 7.1 文档验收

- 目录均有职责，当前与未来路径明确区分，没有将未来能力描述为实现事实。
- 同时说明整体架构、RAG 三层与 MVVM 的不同适用范围。
- 每种公共类型、规则、运行状态和数据均有唯一归属。
- 静态依赖规则闭合、无环，明确基础设施与组装入口的方向。
- 保持六算子、版本过滤、显式错误和独立记录约束。

### 7.2 骨架与后续实现验收

| 检查 | 验证内容 |
|---|---|
| 导入与隔离 | contracts 仅用标准库；核心无 Qt、ORM、模型 SDK；不依靠重导出或 TYPE_CHECKING 绕过规则 |
| 单向依赖 | 目录与包内部无循环；外部只能经 knowledge.api；RAG 仅逐层调用 |
| 无导入副作用 | 导入不连数据库、不加载模型、不启动线程或服务 |
| 可替换性 | 同一套契约用例验证假实现与真实适配器的输出、错误、候选对齐和副作用边界 |
| 版本资格 | 拒绝不合格内容；请求锁定版本、时间、语料与配置；各通道范围一致 |
| 调度与收尾 | 成功、空证据、不足、版本不匹配、未知、引用失败、异常、重试耗尽、取消、记录失败均有明确结果 |
| 记录与回放 | 可捕获终态尝试留痕，失败不伪装成功；回放不重新检索；重算另建运行 |
| 数据库边界 | 无自动迁移、create_all 或启动建表；自动验证不执行任何 DDL/DML |
| 桌面隔离（后续） | QML 绑定 ViewModel；后台不直接改 GUI；核心用例无需 Qt 即可验证 |

数据库集成行为通过经审核的测试设计另行验证；不得以测试名义绕过数据库操作禁令。当前可用假存储、SQL 编译及映射检查验证代码，不自动建立或填充测试数据库。

## 8. 实验记录与结果

本次交付为文档，核对对象是仓库中的产品讨论、技术选型、总体架构及开发规范。仓库目前无应用实现，本文未执行业务链路、模型推理、数据库操作或性能评测。

文档静态验收检查统一模板章节、相对链接和代码围栏，并核对六算子顺序、依赖方向、公共契约归属及当前/后续能力边界。业务、导入图和 MVVM 的运行验收需在相应代码实现后执行；本文不声明召回率、耗时、显存或游戏事实已经验证。

## 9. 设计决策与取舍

| 决策 | 理由与代价 |
|---|---|
| 模块化单体 | 当前聚焦知识与问答，无跨服务部署需求；接受包内边界需持续检查的成本 |
| 六边形架构 | 数据库、模型、脚本和后续桌面可替换；只为当前真实调用定义小端口，避免通用框架 |
| contracts 集中、按职责拆分 | 满足标准库隔离和契约唯一；禁止成为共享杂物包，内部类型不提升为公共契约 |
| knowledge.api 单入口 | 隐藏领域内部组织，控制跨模块调用；仅做明确导出与必要业务组合，不逐层机械转发 |
| 保留三层六算子 | 调度、阶段与可替换执行职责明确；模块层只承担有意义的阶段衔接，不复制算法 |
| 最终 MVVM | 适配 QML 绑定和 Python 用例，隔离界面状态与业务状态；需显式处理线程交付与取消 |
| 按需创建目录 | 避免空骨架、假接口和无实际扩展对象的工厂；保持清晰职责优先于目录数量 |

纯技术分层若允许所有能力共享 ORM 和 service 容易模糊规则归属，因此采用显式领域模块和端口。当前不采用微服务、通用插件发现、服务定位器、事件总线或图 DSL。MVC、MVP 不作为桌面表现层目标；整体工程也不以 MVVM 替代领域和基础设施设计。

SOLID 检查：S 对应每个目录的唯一职责；O 对应算子与端口扩展；L 通过共享契约验证输出、错误和副作用；I 将读写和模型能力按调用方隔离；D 由 bootstrap 把技术实现注入依赖公共契约的核心。抽象以实际变化点和测试替换需求为依据。

## 10. 未解决问题与后续决策

- 公共契约的精确字段、序列化版本和模块内部文件拆分在对应实现任务确定，不能以临时 dict 充当稳定接口。
- 生成供应商、依赖版本、模型 revision、路径和运行配置在实施任务锁定，不在目录设计中猜定。
- 文件/数据库的一致性恢复和记录写入回执需结合真实存储实现验收，不承诺 exactly-once。
- Qt 对象暴露方式、后台执行机制、资源打包和部署验证在桌面任务单独设计。
- OCR、局内状态、路线与受限 Agent 的契约、数据所有权和运行时在需求进入范围后确定；当前不承诺算法或独立 worker。
