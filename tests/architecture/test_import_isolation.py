# -*- coding: utf-8 -*-
"""
文件名：test_import_isolation.py
文件描述: 验证全部模块可导入，且导入期不引入数据库、模型运行库、GUI 与解析实现
作者: 郑智文
创建日期: 2026-11-19
版本: 1.0
IDE: PyCharm
"""

import importlib
import importlib.util
import pkgutil
import sys

# 核心层在导入期不得引入的技术依赖：数据库、模型运行库、GUI 与解析实现。
FORBIDDEN_MODULES = (
    "bm25s",
    "jieba",
    "markdown_it",
    "pgvector",
    "psycopg",
    "pydantic",
    "PySide6",
    "sentence_transformers",
    "sqlalchemy",
    "torch",
)


def _iter_module_names() -> list[str]:
    spec = importlib.util.find_spec("isa")
    if spec is None or spec.submodule_search_locations is None:
        return []
    locations = list(spec.submodule_search_locations)
    return [info.name for info in pkgutil.walk_packages(locations, prefix="isa.")]


def test_modules_import_without_third_party_dependency() -> None:
    names = _iter_module_names()
    assert names, "未发现 isa 子模块，检查 src 布局与 pythonpath 配置"

    for name in names:
        importlib.import_module(name)

    imported = sorted(name for name in FORBIDDEN_MODULES if name in sys.modules)
    assert imported == [], f"导入期引入了被禁止的技术依赖：{imported}"
