<!--
# -*- coding: utf-8 -*-
文件名：README.md
文件描述: 与最终 ORM 一致的完整手工 SQL 说明
作者: 郑智文
创建日期: 2026-11-19
版本: 1.0
IDE: PyCharm
-->

# 手工 SQL

保存与 `src/isa/infrastructure/postgres/models` 最终 ORM 一致的完整 SQL，包括字段、类型、默认值、注释、索引与约束。

约束：

- 只保存结构脚本，不提供自动执行入口；
- 应用启动、安装与测试过程不建表、不迁移、不写入种子数据；
- 需要变更结构时，先在 ORM 与设计层确认，再输出完整 SQL，由用户手动在 PostgreSQL 执行。
