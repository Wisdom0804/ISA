# -*- coding: utf-8 -*-
"""
文件名：enums.py
文件描述: 共享枚举的唯一来源，覆盖审核、文档生命周期、来源、证据、检索、执行与评测值域
作者: 郑智文
创建日期: 2026-11-19
版本: 1.0
IDE: PyCharm
"""

from enum import StrEnum

__all__ = [
    "ChainLifecycle",
    "ClaimType",
    "DatasetStatus",
    "DocumentKind",
    "DocumentStatus",
    "EmbeddingSpaceStatus",
    "EvalCaseKind",
    "EvalVerdict",
    "EvidenceKind",
    "Outcome",
    "RecordStatus",
    "RerankMode",
    "RetrievalChannel",
    "ReviewStatus",
    "RunStatus",
    "SourceType",
    "StepStatus",
]


# ---- 知识审核与文档生命周期 ----

class ReviewStatus(StrEnum):
    """知识对象的审核结论；approved 只表示审核通过，不代表 active。"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DocumentStatus(StrEnum):
    """文档文本的生命周期；superseded 仍退出当前检索。"""

    DRAFT = "draft"
    PUBLISHED = "published"
    SUPERSEDED = "superseded"


class DocumentKind(StrEnum):
    """文档用途。"""

    KNOWLEDGE = "knowledge"


# ---- 来源与声明 ----

class SourceType(StrEnum):
    """逻辑来源的登记类型。"""

    WEB = "web"
    LOCAL_FILE = "local_file"
    NOTE = "note"


class ClaimType(StrEnum):
    """结构化声明的类别。"""

    FACT = "fact"
    RULE = "rule"
    STRATEGY = "strategy"


class EvidenceKind(StrEnum):
    """检索与证据快照使用的知识类型。"""

    CLAIM = "claim"
    GUIDE = "guide"


# ---- 检索 ----

class RetrievalChannel(StrEnum):
    """候选来源通道；术语精确命中只扩展 BM25 查询，不单独成通道。"""

    DENSE = "dense"
    BM25 = "bm25"
    FUZZY = "fuzzy"


class RerankMode(StrEnum):
    """精排模式；disabled 仅用于显式实验或配置降级，并记录事件。"""

    CROSS_ENCODER = "cross_encoder"
    DISABLED = "disabled"


# ---- 执行 ----

class ChainLifecycle(StrEnum):
    """调度进度；completed 不等于业务成功。"""

    INITIALIZED = "initialized"
    RUNNING = "running"
    FINALIZING = "finalizing"
    COMPLETED = "completed"


class StepStatus(StrEnum):
    """单次尝试的技术状态；成功但空结果由 Outcome 表达。"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class Outcome(StrEnum):
    """算子或整条链路的业务结果。"""

    SUCCESS = "success"
    EMPTY_EVIDENCE = "empty_evidence"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    VERSION_MISMATCH = "version_mismatch"
    CITATION_INVALID = "citation_invalid"
    UNKNOWN = "unknown"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecordStatus(StrEnum):
    """业务留痕结果，独立于生成与引用校验状态。"""

    NOT_STARTED = "not_started"
    WRITING = "writing"
    STORED = "stored"
    FAILED = "failed"


class RunStatus(StrEnum):
    """问答、检索与评测运行的执行状态；终态后重试另建 run。"""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmbeddingSpaceStatus(StrEnum):
    """向量空间的生命周期。"""

    BUILDING = "building"
    ACTIVE = "active"
    RETIRED = "retired"


# ---- 评测 ----

class DatasetStatus(StrEnum):
    """评测数据集状态；固定评测运行仅使用 frozen 数据集。"""

    DRAFT = "draft"
    FROZEN = "frozen"
    RETIRED = "retired"


class EvalCaseKind(StrEnum):
    """评测用例类型。"""

    RETRIEVAL = "retrieval"
    ANSWER = "answer"


class EvalVerdict(StrEnum):
    """单例评测判定。"""

    PASS = "pass"
    FAIL = "fail"
    NOT_SCORED = "not_scored"
