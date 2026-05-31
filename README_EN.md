# MCP-Embedded-Helper

> An MCP-based AI toolchain for embedded Linux developers — gives AI "eyes and hands" to analyze cross-compile errors and diagnose development environments.

**[中文 →](README.md)**

---

## Why

Cross-compile errors are cryptic, device tree syntax is error-prone, and kernel Oops logs are unreadable hex dumps.  
General AI assistants don't understand `arm-linux-gcc` error patterns or `.dts` node rules.

This project gives AI embedded-development-specific tools:
- **Eyes** — read build logs, source files, and environment config
- **Hands** — execute make, parse errors, diagnose environments, gather source context

---

## Features

- **Cross-Compile Analyzer** — Auto-runs `make`, parses `arm-linux-gcc` output, identifies 7 error types with FATAL / ERROR / WARNING severity, and collects source code context around each error
- **Environment Doctor** — Checks `CROSS_COMPILE`, `ARCH`, `CC` env vars, auto-scans for cross-compilers, verifies make version
- **Device Tree Generator** (WIP) — Generate `.dts` node code for specific SoCs
- **Kernel Oops Decoder** (WIP) — Translate hex callstacks into `filename + line number`

---

## Environment Diagnosis

Auto-detects the following cross-compiler toolchain prefixes:

```
arm-linux-gnueabihf- | arm-linux-gnueabi- | aarch64-linux-gnu-
arm-buildroot-linux-gnueabihf- | arm-none-eabi- | arm-linux-
riscv64-linux-gnu- | mips-linux-gnu-
```

---

## Quick Start

### 1. Clone

```bash
git clone git@github.com:w4ysonch/MCP-Embedded-Helper.git
cd MCP-Embedded-Helper
```

### 2. Install Dependencies

```bash
pip install mcp[cli]
```

### 3. Run Tests

```bash
python tests/test_error_parser.py
python tests/test_env_checker.py
python tests/test_context_gatherer.py
python tests/test_build_runner.py
```

### 4. Wire Up with Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "embedded-helper": {
      "command": "python",
      "args": ["src/main.py"],
      "cwd": "/path/to/MCP-Embedded-Helper"
    }
  }
}
```

Restart Claude Code. The tools below will be available.

### 5. Usage

In the Claude Code dialog:

> "Use run_build_and_analyze to compile this project and analyze any errors"

Or:

> "Check my cross-compile environment"

Claude will invoke your tools and return the analysis.

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `run_build_and_analyze` | Run `make`, capture output, analyze errors with source context |
| `analyze_build_error` | Analyze build error text or log file |
| `check_cross_env` | Diagnose cross-compile environment |
| `list_files` | List current directory contents |

---

## Error Types Recognized

| Type | Severity | Pattern |
|------|----------|---------|
| `syntax_error` | ERROR | `expected ';'`, `undeclared`, `implicit declaration` |
| `linker_error` | ERROR | `undefined reference to`, `cannot find -l`, `ld returned 1` |
| `header_missing` | ERROR | `fatal error: xxx.h: No such file` |
| `arch_mismatch` | ERROR | `skipping incompatible`, `wrong architecture` |
| `make_error` | ERROR | `make[1]: *** [target] Error` |
| `toolchain_missing` | FATAL | `arm-linux-gcc: Command not found` |
| `warning` | WARNING | `unused variable`, `no return statement`, etc. |

---

## Project Structure

```
MCP-Embedded-Helper/
├── src/
│   ├── main.py                # MCP Server entry point
│   ├── tools/                 # MCP tool layer (LLM-callable interfaces)
│   │   └── build_analyzer.py  #   Build analysis + env doctor tools
│   ├── core/                  # Core logic (MCP-decoupled, testable)
│   │   ├── error_parser.py    #   Build error parser (regex + structured)
│   │   ├── context_gatherer.py #  Source context collector
│   │   ├── build_runner.py    #   make build executor
│   │   └── env_checker.py     #   Cross-compile environment doctor
│   └── config/                # Configuration
│       └── settings.py        #   Toolchain prefixes, env var names
├── tests/
│   ├── fixtures/              # Test fixtures
│   │   ├── sample_arm_gcc_errors.txt
│   │   └── sample_led_drv.c
│   ├── test_error_parser.py   #   11 tests
│   ├── test_env_checker.py    #   5 tests
│   ├── test_context_gatherer.py # 8 tests
│   └── test_build_runner.py   #   8 tests
├── requirements.txt
├── README.md
└── README_EN.md
```

---

## Architecture

```
Claude Code
        │
        ▼
   main.py  ←—— MCP entry point (4 tools)
        │
        ▼
   tools/build_analyzer.py  ←—— MCP tool layer
        │
        ├── core/error_parser.py     ←—— Parse build output → structured data
        ├── core/context_gatherer.py  ←—— Locate source → snippet context
        ├── core/build_runner.py     ←—— Run make → capture output
        └── core/env_checker.py      ←—— Diagnose env → report
```

---

## Tech Stack

| Component | Description |
|-----------|-------------|
| Python 3.x | Language |
| FastMCP | MCP Server framework |
| Regex | Error pattern matching |
| Claude Code | MCP-compatible AI client |

---

## License

MIT License
