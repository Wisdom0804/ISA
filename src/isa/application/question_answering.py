# -*- coding: utf-8 -*-
"""
文件名：question_answering.py
文件描述: 问答入口用例，冻结请求上下文并调用 RAG 编排，统一处理业务结果与记录收尾
作者: 郑智文
创建日期: 2026-11-19
版本: 1.0
IDE: PyCharm
"""

# 请求开始时固定 scope、as_of、evidence_kinds、active selection 与配置快照；运行期间不重新选择。
