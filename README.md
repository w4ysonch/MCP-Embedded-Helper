# MCP-Embedded-Helper

> 基于 MCP 协议的嵌入式 Linux 开发辅助工具链 — 让 AI 拥有"手和眼"帮你分析交叉编译报错、诊断开发环境。

**[English →](README_EN.md)**

---

## 为什么需要它

交叉编译报错晦涩难懂、设备树语法容易写错、内核 Oops 是一堆天书般的十六进制。  
通用 AI 助手不懂 `arm-linux-gcc` 的错误模式，也不知道设备树的节点规范。

这个项目为 AI 提供嵌入式开发专用的"眼和手"：
- **眼** — 读取你的编译日志、源码文件、环境配置
- **手** — 自动执行 make、解析错误、诊断环境、收集源码上下文

---

## 功能

- **交叉编译分析器** — 自动执行 `make` 编译，解析 `arm-linux-gcc` 报错，识别 7 种错误类型，标记 FATAL / ERROR / WARNING 三个严重级别，并自动收集报错位置的源文件上下文
- **一键环境诊断** — 检查 `CROSS_COMPILE`、`ARCH`、`CC` 环境变量，自动扫描系统中的交叉编译器，检测 make 版本
- **设备树生成**（开发中） — 根据芯片型号自动生成 `.dts` 节点代码
- **内核 Oops 解码**（开发中） — 把十六进制调用栈翻译成 文件名 + 行号

---

## 环境诊断功能

支持自动扫描以下交叉编译链前缀：

```
arm-linux-gnueabihf- | arm-linux-gnueabi- | aarch64-linux-gnu-
arm-buildroot-linux-gnueabihf- | arm-none-eabi- | arm-linux-
riscv64-linux-gnu- | mips-linux-gnu-
```

---

## 安装

```bash
pip install mcp-embedded-helper
```

### 源码安装

```bash
git clone git@github.com:w4ysonch/MCP-Embedded-Helper.git
cd MCP-Embedded-Helper
pip install -e .
```

### 运行测试

```bash
python tests/test_error_parser.py
python tests/test_env_checker.py
python tests/test_context_gatherer.py
python tests/test_build_runner.py
```

### 接入 Claude Code

在 `.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "embedded-helper": {
      "command": "mcp-embedded-helper",
      "args": []
    }
  }
}
```

重启 Claude Code 后即可使用。在对话框中说：

> "用 run_build_and_analyze 编译这个项目并分析报错"

或者：

> "检查一下我的交叉编译环境"

---

## MCP 工具列表

| 工具名 | 功能 |
|--------|------|
| `run_build_and_analyze` | 执行 `make` 编译，自动捕获输出并分析错误，附带源码上下文 |
| `analyze_build_error` | 分析已有的编译报错文本或日志文件 |
| `check_cross_env` | 一键诊断交叉编译环境 |
| `list_files` | 列出当前目录文件 |

---

## 识别错误类型

| 类型 | 严重级别 | 典型特征 |
|------|---------|---------|
| `syntax_error` | ERROR | `expected ';'`, `undeclared`, `implicit declaration` |
| `linker_error` | ERROR | `undefined reference to`, `cannot find -l`, `ld returned 1` |
| `header_missing` | ERROR | `fatal error: xxx.h: No such file` |
| `arch_mismatch` | ERROR | `skipping incompatible`, `wrong architecture` |
| `make_error` | ERROR | `make[1]: *** [target] Error` |
| `toolchain_missing` | FATAL | `arm-linux-gcc: Command not found` |
| `warning` | WARNING | `unused variable`, `no return statement` 等 |

---

## 项目结构

```
MCP-Embedded-Helper/
├── src/mcp_embedded_helper/
│   ├── main.py                # MCP Server 入口
│   ├── tools/                 # MCP 工具层
│   │   └── build_analyzer.py  #   编译分析 + 环境诊断
│   ├── core/                  # 核心逻辑层
│   │   ├── error_parser.py    #   编译报错解析
│   │   ├── context_gatherer.py #  源文件上下文
│   │   ├── build_runner.py    #   make 构建执行
│   │   └── env_checker.py     #   环境诊断
│   └── config/settings.py     # 工具链配置
├── tests/                      # 32 个单元测试
├── pyproject.toml              # pip 包配置
├── README.md
└── README_EN.md
```

---

## 架构

```
Claude Code 对话框
        │
        ▼
   main.py  ←—— MCP 入口（4 个工具）
        │
        ▼
   tools/build_analyzer.py  ←—— MCP 工具层
        │
        ├── core/error_parser.py     ←—— 报错文本 → 结构化数据
        ├── core/context_gatherer.py  ←—— 定位源文件 → 截取上下文
        ├── core/build_runner.py     ←—— 执行 make → 捕获输出
        └── core/env_checker.py      ←—— 检测环境 → 诊断报告
```

---

## 技术栈

| 组件 | 说明 |
|------|------|
| Python 3.x | 开发语言 |
| FastMCP | MCP Server 框架 |
| Regex | 编译报错模式匹配 |
| Claude Code | 支持 MCP 协议的 AI 客户端 |

---

---

## 常见问题

### pip install 报错: Could not find a version

要求 Python >= 3.9。执行 `python3 --version` 确认版本。如果版本过低，升级 Python：

```bash
# Ubuntu
sudo apt update && sudo apt install python3.10 python3-pip

# macOS
brew install python@3.10
```

### pip: command not found

```bash
# Ubuntu
sudo apt install python3-pip

# macOS (随 Homebrew Python 自动安装)
```

### SSL 连接报错

确保系统开启了 SSL 支持：
```bash
sudo apt install ca-certificates libssl-dev
python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"  # 确认 SSL 可用
```

---

## 许可

MIT License
