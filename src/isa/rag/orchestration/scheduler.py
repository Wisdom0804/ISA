# -*- coding: utf-8 -*-
"""
文件名：scheduler.py
文件描述: 状态转换、结果接纳与统一收尾
作者: 郑智文
创建日期: 2026-11-19
版本: 1.0
IDE: PyCharm
"""

# ChainState 只在此受控更新；算子只返回 OperatorResult，不指定任意下一步。
# 成功、空证据、不足、版本不匹配、未知、引用失败、异常、重试耗尽与取消都进入同一 finalizing 规则。
