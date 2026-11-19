# ISA 决策助手：官方资料核验记录

工具资料核验基准为 2026-11-16；共享枚举和数据库约束依据见表内官方文档。事实列描述工具能力；项目含义说明其与当前项目范围的关系，不代表本机安装或性能已验证。项目边界以[项目讨论与开发决策](project-discussion.md)为准，模块与数据模型以[ISA 架构设计文档](isa-architecture-design.md)为准，本文件不另设一套参数。

当前项目范围是《黑流树海》知识库和有引用的问答闭环，通过 Python 开发脚本和测试调用应用用例。知识管理、审核、版本选择、混合检索、回答、引用校验和运行记录构成当前架构；桌面交互、OCR、局面识别与路线决策不属于当前实现范围。基础设施工具能力不构成业务模块，也不表示工具已部署。

## 已核验事实

| 来源 | 官方资料中确认的事实 | 对本项目的含义 |
|---|---|---|
| [pgvector README](https://github.com/pgvector/pgvector) | pgvector 是 PostgreSQL 扩展，可把向量与业务数据放在同一数据库；支持精确近邻搜索、HNSW 与 IVFFlat 近似索引、过滤条件、半精度/二进制/稀疏向量。HNSW 通常有更好的速度-召回折中但建索引更慢且更占内存；IVFFlat 建索引更快且占用更少但折中较弱。 | 当前技术选型采用 PostgreSQL 与 pgvector 保存规范关系数据和向量；近似索引结果需在实现评测中与精确查询比较。该工具事实不表示已安装或索引已建成。 |
| [PostgreSQL 16 text search parser](https://www.postgresql.org/docs/16/textsearch-parsers.html) | 原生 parser 负责把文本拆为 token，并受数据库 locale (`lc_ctype`) 影响；该页没有提供面向中文的词法分词器。 | 当前 BM25 词法召回由所选 Python 实现承担；PostgreSQL 原生全文检索不替代该方案。 |
| [PostgreSQL 16 `pg_trgm` documentation](https://www.postgresql.org/docs/16/pgtrgm.html) | `pg_trgm` 的相似度基于连续字符组成的 trigram，并忽略非单词字符；提供 GiST/GiN 索引和相似度/模糊匹配操作符。它不是中文词边界或语义分词器。 | 项目设计将其作为独立 `fuzzy` 候选通道参与融合，不替代 BM25 词法召回；术语精确命中仅扩展 BM25 查询。 |
| [Trafilatura README](https://github.com/adbar/trafilatura) | Python 包/CLI；可下载或处理 HTML，提取正文、标题、作者、日期、站点、标签等元数据，支持 Markdown/JSON/HTML/XML 等输出；不需要数据库；当前包 Apache-2.0，v1.8.0 之前为 GPLv3+。 | 网页自动采集不属于当前导入范围；若未来采用该工具，保留原始来源快照并核对实际版本许可证。 |
| [PaddleOCR README](https://github.com/PaddlePaddle/PaddleOCR) | 官方称支持 Windows/Linux/macOS、CPU/GPU 等后端；可把 PDF/图片转为面向 LLM 的 JSON/Markdown，PP-StructureV3 提供结构/坐标信息；支持中文等多语言；许可证为 Apache-2.0。 | OCR 不在当前范围内；官方平台支持不证明对 ISA 资料或游戏画面识别准确，未来采用前需用目标样本验证并保留人工确认。 |
| [RAGFlow README](https://github.com/infiniflow/ragflow) | 提供复杂文档解析、模板化切块、多路召回/融合重排、可追溯引用、Word/PPT/Excel/TXT/图片/PDF/扫描件/网页等异构资料支持。官方 Docker 起步建议 4 CPU、16 GB RAM、50 GB 磁盘；实际取决于解析、数据量、并发和本地模型；Docker ≥24、Compose ≥2.26.1。v1.0 文档称 DeepDoc 的版面分析/OCR/表格识别使用 CPU。仓库 LICENSE 为 Apache-2.0。 | RAGFlow 不属于当前依赖或预定试验；其功能说明和资源建议不代表 ISA 的安装、兼容性或质量结论。 |
| [Dify README](https://github.com/langgenius/dify) | 提供文档导入和 RAG 能力，README 写明支持 PDF、PPT 等常见格式；自托管 Docker Compose 最低要求 CPU ≥2 core（其余内存/磁盘以官方文档和 compose 为准）。 | Dify 不属于当前依赖或预定试验；其官方能力不替代 ISA 已选的领域数据模型和固定 RAG 契约。 |
| [Dify LICENSE](https://github.com/langgenius/dify/blob/main/LICENSE) | 不是纯 Apache-2.0：为 Apache-2.0 加额外条件，包括多租户限制以及前端 Logo/版权信息限制；商业/对外服务前需逐条核对。 | 个人本地使用通常问题较少；多人或商业部署必须先做许可证审查。 |
| [BGE-M3 model card](https://huggingface.co/BAAI/bge-m3) | MIT；支持 100+ 语言、最长 8192 tokens，同时支持 dense、sparse、multi-vector；作者推荐 hybrid retrieval + re-ranking，并说明 cross-encoder reranker 通常比单纯 bi-encoder 更准。模型表列出 1024 维。 | 技术选型采用本地 BGE-M3 dense 1024 维；模型卡不证明本机兼容、性能或项目检索质量，云端 embedding 不进入规范向量空间。 |
| [SQLAlchemy 2.0 documentation](https://docs.sqlalchemy.org/en/20/) | 官方文档同时覆盖 ORM 和 Core 两套 SQL 工具，SQLAlchemy 以 MIT 许可发布。 | 技术选型采用 SQLAlchemy 2.x ORM；向量距离、RRF 融合和批量查询可使用 Core 或绑定参数 SQL。 |
| [Python 3.12 enum](https://docs.python.org/3.12/library/enum.html) | StrEnum 的成员也是字符串，适合显式字符串常量。 | 架构设计采用显式字符串枚举表达审核、生命周期、运行结果和证据类型；代码尚未实现。 |
| [PostgreSQL 16 enum types](https://www.postgresql.org/docs/16/datatype-enum.html) | 原生枚举已存在的值不能直接删除或重新排序，须删除并重建类型。 | 架构采用文本列与具名 CHECK 约束表达受控值域；数据库结构由用户手动执行完整 SQL，不执行自动迁移。 |

## 选型结论（工程判断）

1. **当前技术组合**：选型为 Python 模块化单体、PostgreSQL 16/pgvector、BGE-M3 dense 1024 维、HNSW 和本地文件保存原件；这些是目标技术方案，不表示安装、部署或验收已完成。云端 embedding 不写入规范向量空间。
2. **知识库检索**：当前默认流程为 BM25 与 Dense 召回、RRF 融合及 Cross-Encoder 精排，可按配置加入独立 fuzzy 通道。术语精确命中作为 BM25 查询扩展。中文词法实现、索引清单和模型 revision 按[技术选型决策](technology-selection.md)锁定并在实施时验证；知识维护独立于单次问答。
3. **存储边界**：关系数据和向量使用 PostgreSQL/pgvector，原始文件通过哈希和快照引用关联。暂不引入独立向量库、搜索集群或微服务；若未来评测和运行约束证明必要，再单独确认。
4. **证据与版本**：sources 保存逻辑来源，source_snapshots 保存捕获 URI、时间和内容哈希；`active_document_selections` 按 source/scope 指向当前 document，审核通过不自动激活。documents/chunks 保存版本、审核、适用范围和来源定位；`as_of` 筛选适用时间，`evidence_kinds` 区分 claim 与 guide 资格。默认问答只使用 active、已审核、版本匹配且来源合格的证据。
5. **数据库边界**：ORM/设计与手工 SQL 必须一致。应用、测试和安装流程不得自动建表、迁移或写入数据库；结构变更由用户手动执行 SQL。
6. **未来能力**：桌面、OCR、局面和路线决策不属于当前问答架构。工具可作为未来候选参考，不据此预设当前部署、进程隔离、数据模型或路线算法。

## 限制与待验证项

- 工具表是带核验基准的能力参考，不是最新版本清单；RAGFlow/Dify 不属于当前依赖，部署其他工具时也须锁定实际 release/model revision 并验证兼容性。
- Windows wheel、本地模型加载和 PostgreSQL 扩展组合尚需实施环境验收；官方平台支持不等于具体版本组合已验证。embedding、ANN 和生成不保证跨环境逐字节一致，运行快照用于回放已保存结果。
- 游戏资料可能受网站条款、版权、登录限制影响；采集前检查来源许可，并保留出处。
