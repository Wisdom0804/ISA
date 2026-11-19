# Modular RAG 工具角色与适配核验

核验日期：2026-11-18。范围为官方文档与仓库公开能力；未安装框架或运行性能实验。本文提供选型依据，不改变[项目讨论](project-discussion.md)和[总体架构](isa-architecture-design.md)规定的业务边界。

## 1. 应用需求

ISA 当前先完成知识库与问答用例，通过脚本和测试验证，不开发交互式 CLI 或 Web，保持“编排层 → 模块层 → 算子层”。比较重点是固定调度、类型契约、状态及可追溯记录，不能因框架具备 Agent 能力就提前启用模型自由规划。

## 2. 用户场景与输入输出

输入为问题、`scope/as_of`、允许的 `evidence_kinds`、请求时 active 选择与配置；输出为有证据的回答、可识别错误或未知状态以及完整运行记录。`as_of` 只匹配适用时间，active 选择按 source/scope 由用户显式确定。固定顺序仍为预检索、混合检索、证据过滤、生成、引用校验和独立记录算子。

## 3. 相关技术

| 工具 | 官方定位与能力 | 对 ISA 的含义（工程判断） |
|---|---|---|
| DeepSeek Harness | 确有 DeepSeek AI 官方公开项目，基于 Node.js/Cordis，“一切皆插件”；模型适配器、工具注册、会话日志和 Agent 循环均可替换。[1][2] | 是通用 Agent 运行环境，不能仅按“DeepSeek 模型客户端”理解；当前固定 Python RAG 不需要引入整套运行环境。 |
| Haystack | Pipeline 是组件有向多重图，可显式连接分支、循环及异步流程；自定义组件声明输入/输出并实现 `run()`。[4][5] | 三者中最贴近固定 RAG 编排，可把 ISA 算子包装为组件，但模块划分及领域协议仍由 ISA 持有。 |
| Pydantic AI | Agent 支持类型化依赖与结构化输出；通过 `RunContext` 向工具、指令和校验器传递依赖，用 Pydantic 构造 schema 并校验模型数据。[8][9] | 更适合生成适配器、受控工具调用或未来单个 Agent 算子，不要求接管整条检索流程。 |

## 4. 方案与架构

当前采用 Python 显式流程与类型化状态，Haystack Pipeline 为后期扩展备选。Pydantic AI 仅作工具角色参考，不是当前依赖或既定扩展路线。项目决策以[技术选型决策](technology-selection.md)为准，不应让同一流程同时存在两套调度权威。

DeepSeek Harness 工具定义支持参数推导/校验、规范输出与面向模型的渲染分离。[3] 这些设计可参考，但官方仍标注 developer preview、会破坏兼容，且尚未经安全审计、不可视为 production-ready。[1][11] 当前不选作 ISA 核心编排依赖。

## 5. 数据模型与接口

Haystack Agent 的 `State` 是工具间共享数据、合并结果和保存消息的运行容器；Agent 动态选择工具，与固定 Pipeline 不是同一种调度方式。[6] Pydantic AI 的依赖对象也不自动成为 ISA 不可变运行快照。[9]

`pydantic-graph` 是独立的异步图/状态机库，不依赖 `pydantic-ai`；官方明确图并非所有任务所需。[10] Pydantic、Pydantic AI 与 pydantic-graph 是不同能力层；已有 Pydantic 数据模型不表示已引入 AI 或图框架。

无论使用哪种框架，核心算子仍须声明输入/输出、实现版本、配置快照、证据及副作用边界；框架异常须映射为 ISA 结构化错误，重试与降级须显式配置并记录。schema 校验不能证明引用正确、资料已审核或游戏事实真实。

## 6. 实现步骤

本次交付为资料核验与适配判断，未增加依赖、修改代码或执行数据库命令。后续若试验，只替换一个适配器或组件，先保留原有协议和固定流程，再比较实际收益。

## 7. 验收标准

候选方案须证明：只用 active 且已审核、版本匹配的证据；空证据、版本不匹配及引用失败可识别；核心失败不静默转成功；替换实现不改变编排层契约；失败路径同样进入记录。

## 8. 实验记录与结果

已核对下列官方来源；未测量延迟、召回率、资源占用或 Windows 兼容组合。官方具备某项能力不代表 ISA 已实现或通过验收。

## 9. 设计决策与取舍

框架状态与 ISA `RecordOperator` 分工必须明确：Haystack YAML 保存流程结构，断点快照用于检查、恢复执行；DeepSeek Harness 的追加会话日志用于投影模型历史；它们都不自动满足 ISA 完整业务留痕。[2][7]

`RecordOperator` 仍需封存链路/运行 ID、`scope/as_of/evidence_kinds`、active selection ID 与版本选择依据、实际检索通道和精排模式、算子顺序与配置、召回和最终证据、来源定位、内容哈希、生成请求/响应、错误/未知/重试/降级及耗时。框架日志和恢复快照可作为关联附件，不能替代这些字段，也不能据此承诺模型重算逐字一致。

## 10. 未解决问题与后续决策

当前框架方向为 Python 显式调度、Haystack 后期备选；其他工具保留事实比较，不作为默认迁移路线。引入备选前仍需核验发行版 API、依赖及环境，并用固定案例验证失败传播、状态转换与记录完整性，不扩大初期 Agent 范围。

## 官方来源

1. [DeepSeek Harness README](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.md)
2. [DeepSeek Harness architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
3. [DeepSeek Harness tool tutorial](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/tool.md)
4. [Haystack Pipelines](https://docs.haystack.deepset.ai/docs/pipelines)
5. [Haystack custom components](https://docs.haystack.deepset.ai/docs/custom-components)
6. [Haystack Agent](https://docs.haystack.deepset.ai/docs/agent)；[State](https://docs.haystack.deepset.ai/docs/state)
7. [Haystack serialization](https://docs.haystack.deepset.ai/docs/serialization)；[Pipeline breakpoints](https://docs.haystack.deepset.ai/docs/pipeline-breakpoints)
8. [Pydantic AI output](https://ai.pydantic.dev/output/)
9. [Pydantic AI dependencies](https://ai.pydantic.dev/dependencies/)
10. [pydantic-graph](https://ai.pydantic.dev/graph/)
11. [DeepSeek Harness safety notice](https://github.com/deepseek-ai/deepseek-harness/blob/master/SAFETY.md)
