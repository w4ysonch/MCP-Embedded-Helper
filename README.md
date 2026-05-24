# MCP-Embedded-Helper

AI-powered CLI tools for embedded Linux developers, built on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io).  
基于 MCP 协议的嵌入式 Linux 开发辅助工具链，让大模型拥有"手和眼"帮你解决底层开发痛点。

## Why / 为什么需要它

Cross-compile errors are cryptic, device tree syntax is error-prone, and kernel oops logs are unreadable hex dumps.  
General AI assistants don't understand `arm-linux-gcc` error patterns or `.dts` node rules — they need specialized tools to actually help.

This project gives AI the "eyes and hands" to read your build logs, parse error messages, and gather relevant source  
context, so the LLM can deliver precise root-cause analysis instead of vague suggestions.

交叉编译报错晦涩难懂、设备树语法容易写错、内核 Oops 日志是一堆天书般的十六进制。  
通用 AI 助手不懂 `arm-linux-gcc` 的错误模式，也不知道设备树的节点规范。  
这个项目给 AI 提供了嵌入式开发专用的"眼和手"，让它能读懂你的编译日志、提取关键错误、  
收集源码上下文，从而给出精准的根因分析而不是泛泛而谈的建议。

## Features / 功能

- **交叉编译分析器** — 解析 `arm-linux-gcc` 编译报错，识别 7 种错误类型并提取文件名/行号/错误消息
- **环境诊断**（开发中） — 自动检测 `CROSS_COMPILE`、`ARCH` 等环境变量是否正确配置
- **设备树生成**（开发中） — 根据芯片型号自动生成符合规范的 `.dts` 节点代码
- **内核 Oops 解码**（开发中） — 把十六进制调用栈翻译成 `文件名 + 行号`

## Quick Start / 快速开始

```bash
# 1. Clone
git clone git@github.com:w4ysonch/MCP-Embedded-Helper.git
cd MCP-Embedded-Helper

# 2. Install dependencies
pip install mcp[cli]

# 3. Configure Claude Code
# 在 .claude/settings.json 中添加:
# {
#   "mcpServers": {
#     "embedded-helper": {
#       "command": "python",
#       "args": ["src/main.py"],
#       "cwd": "<你的项目路径>"
#     }
#   }
# }

# 4. Run tests
python tests/test_error_parser.py
```

## Project Structure / 项目结构

```
MCP-Embedded-Helper/
├── src/
│   ├── main.py              # MCP 入口，注册所有工具
│   ├── tools/               # MCP 工具层（对外暴露给大模型的接口）
│   ├── core/                # 核心逻辑层（错误解析、上下文收集、构建执行）
│   │   └── error_parser.py  # 编译报错结构化解析
│   └── config/              # 工具链路径、预设模式等配置
├── tests/
│   ├── fixtures/            # 测试用的示例报错日志
│   └── test_error_parser.py
└── requirements.txt
```

## Tech Stack / 技术栈

| 组件 | 说明 |
|------|------|
| Python 3.x | 开发语言 |
| [FastMCP](https://github.com/jlowin/fastmcp) | MCP Server 框架 |
| Regex | 编译报错模式匹配 |
| Claude Code / Cursor / Continue | 支持 MCP 协议的 AI 客户端 |
