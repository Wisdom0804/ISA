# -*- coding: utf-8 -*-
"""
文件名：replay_run.py
文件描述: 按 run_id 读取历史封存结果，不重新检索
作者: 郑智文
创建日期: 2026-11-19
版本: 1.0
IDE: PyCharm
"""

from __future__ import annotations

import sys
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """读取指定运行的封存输入、证据与输出；重算另建运行。"""
    raise NotImplementedError("回放用例接入后实现")


if __name__ == "__main__":
    sys.exit(main())
