# -*- coding: utf-8 -*-
"""
文件名：__init__.py
文件描述: 问答流水线包，保持编排层、模块层、算子层三层边界
作者: 郑智文
创建日期: 2026-11-19
版本: 1.0
IDE: PyCharm
"""

# 固定顶层顺序：QueryPrecheck → HybridRetrieve → EvidenceFilter → AnswerGenerate
# → CitationValidate → Record。

__all__: tuple[str, ...] = ()
