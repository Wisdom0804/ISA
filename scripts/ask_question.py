# -*- coding: utf-8 -*-
"""
文件名：ask_question.py
文件描述: 调用问答用例，输出回答、引用、未知项与运行结果
作者: 郑智文
创建日期: 2026-11-19
版本: 1.0
IDE: PyCharm
"""

from __future__ import annotations

import sys
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """解析参数，调用 QuestionAnswering.answer 并输出结构化问答结果。"""
    raise NotImplementedError("问答用例接入后实现")


if __name__ == "__main__":
    sys.exit(main())
