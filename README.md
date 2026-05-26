# MCP-Embedded-Helper

> 基于 MCP 协议的嵌入式 Linux 开发辅助工具链 — 让 AI 拥有"手和眼"帮你分析交叉编译报错、诊断开发环境。

**[English →](README_EN.md)**

---

## 为什么需要它

交叉编译报错晦涩难懂、设备树语法容易写错、内核 Oops 是一堆天书般的十六进制。  
通用 AI 助手不懂 `arm-linux-gcc` 的错误模式，也不知道设备树的节点规范。

这个项目为 AI 提供嵌入式开发专用的"眼和手"：
- **眼** — 读取你的编译日志、源码文件、环境配置
- **手** — 自动解析错误、诊断环境、收集上下文

让大模型从"泛泛而谈"变成精准的根因分析和修复建议。

---

## 功能

- **交叉编译分析器** — 解析 `arm-linux-gcc` 编译报错，识别 7 种错误类型，标记 FATAL / ERROR / WARNING 三个严重级别
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

## 快速开始

### 1. 克隆仓库

```bash
git clone git@github.com:w4ysonch/MCP-Embedded-Helper.git
cd MCP-Embedded-Helper
```

### 2. 安装依赖

```bash
pip install mcp[cli]
```

### 3. 运行测试

```bash
python tests/test_error_parser.py
python tests/test_env_checker.py
```

### 4. 接入 Claude Code

在 `.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "embedded-helper": {
      "command": "python",
      "args": ["src/main.py"],
      "cwd": "/你的项目路径/MCP-Embedded-Helper"
    }
  }
}
```

重启 Claude Code 后即可使用 `analyze_build_error`、`check_cross_env`、`list_files` 三个工具。

### 5. 使用示例

在 Claude Code 对话框中说：

> "帮我分析这段编译报错：drivers/led.c:42:5: error: expected ';' before '}' token"

或者：

> "检查一下我的交叉编译环境"

Claude 会自动调用你的工具并返回分析结果。

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
├── src/
│   ├── main.py                # MCP Server 入口，注册所有工具
│   ├── tools/                 # MCP 工具层（暴露给大模型的接口）
│   │   └── build_analyzer.py  #   交叉编译分析 + 环境诊断工具
│   ├── core/                  # 核心逻辑层（与 MCP 解耦，可独立测试）
│   │   ├── error_parser.py    #   编译报错解析（正则 + 结构化输出）
│   │   └── env_checker.py     #   环境诊断（工具链/变量/make 检测）
│   └── config/                # 配置
│       └── settings.py        #   工具链前缀、环境变量常量
├── tests/
│   ├── fixtures/              # 测试用的示例报错日志
│   │   └── sample_arm_gcc_errors.txt
│   ├── test_error_parser.py   #   11 个单元测试
│   └── test_env_checker.py    #   5 个单元测试
├── requirements.txt
├── README.md
└── README_EN.md
```

---

## 架构

```
Claude Code 对话框
        │
        ▼
   main.py  ←—— MCP 入口
        │
        ▼
   tools/build_analyzer.py  ←—— MCP 工具层（AI 调用的接口）
        │
        ▼
   core/error_parser.py     ←—— 解析报错文本 → 结构化数据
   core/env_checker.py      ←—— 检测系统环境 → 诊断报告
        │
   config/settings.py       ←—— 常量配置
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

## 许可

MIT License
