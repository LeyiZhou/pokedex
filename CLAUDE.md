# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

宝可梦对战速查工具。包含两部分：离线数据管线（Python/Node.js 脚本从 Smogon/PokeAPI/Showdown 获取数据并生成 JSON）+ 纯静态单页前端（`web/index.html`，无框架、无构建步骤）。

## 数据管线运行顺序

```bash
# 1. 从 Pokemon Showdown GitHub 下载原始 .ts 数据文件
python3 fetch_showdown.py

# 2. 将 .ts 文件解析为 JSON
node parse_data.js

# 3. 生成权威属性克制表
python3 gen_typechart.py

# 4. 生成宝可梦/招式中文名映射
python3 gen_cn_names.py

# 5. 生成道具/树果/术语中文名映射
python3 gen_cn_terms.py

# 6. 从 Smogon 获取对战配表（需要代理 127.0.0.1:7890，支持断点续传）
python3 fetch_sets.py
```

## 运行前端

直接用浏览器打开 `web/index.html`，或使用任意静态 HTTP 服务器。`web/data` 是指向 `../data` 的符号链接。

## 架构要点

- **零依赖**：所有脚本仅使用 Python/Node.js 标准库，前端仅使用原生 JS
- **双语数据模型**：所有实体以英文（Showdown 格式）为 key，中文名通过独立 JSON 映射文件维护（`*_cn.json`），前端运行时合并
- **数据源**：Showdown GitHub 仓库的 TypeScript 文件 → 自定义状态机解析器（`parse_data.js`）→ JSON
- **属性克制表**：`gen_typechart.py` 生成的 `typechart_clean.json` 是权威版本；Showdown 原始编码（0=0.5x, 1=1x, 2=2x, 3=免疫）需转换
- **网络代理**：`fetch_data.py`、`fetch_sets.py`、`fetch_showdown.py` 硬编码使用 `http://127.0.0.1:7890` 代理
