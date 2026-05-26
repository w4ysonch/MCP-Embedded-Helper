# MCP-Embedded-Helper

> An MCP-based AI toolchain for embedded Linux developers — gives AI "eyes and hands" to analyze cross-compile errors and diagnose development environments.

**[中文 →](README.md)**

---

## Why

Cross-compile errors are cryptic, device tree syntax is error-prone, and kernel Oops logs are unreadable hex dumps.  
General AI assistants don't understand `arm-linux-gcc` error patterns or `.dts` node rules.

This project gives AI embedded-development-specific tools:
- **Eyes** — read build logs, source files, and environment config
- **Hands** — parse errors, diagnose environments, gather context

So the LLM can deliver precise root-cause analysis instead of vague suggestions.

---

## Features

- **Cross-Compile Analyzer** — Parses `arm-linux-gcc` build output, identifies 7 error types, marks each with FATAL / ERROR / WARNING severity
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

Restart Claude Code. Three tools will be available: `analyze_build_error`, `check_cross_env`, `list_files`.

### 5. Usage

In the Claude Code dialog:

> "Analyze this build error: drivers/led.c:42:5: error: expected ';' before '}' token"

Or:

> "Check my cross-compile environment"

Claude will invoke your tools and return the analysis.

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
│   │   └── build_analyzer.py  #   Build error analysis + env doctor
│   ├── core/                  # Core logic (MCP-decoupled, testable)
│   │   ├── error_parser.py    #   Build error parser (regex + struct output)
│   │   └── env_checker.py     #   Environment doctor
│   └── config/                # Configuration
│       └── settings.py        #   Toolchain prefixes, env var names
├── tests/
│   ├── fixtures/              # Sample build error logs
│   │   └── sample_arm_gcc_errors.txt
│   ├── test_error_parser.py   #   11 unit tests
│   └── test_env_checker.py    #   5 unit tests
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
   main.py  ←—— MCP entry point
        │
        ▼
   tools/build_analyzer.py  ←—— MCP tool layer (AI-callable)
        │
        ▼
   core/error_parser.py     ←—— Parse build output → structured data
   core/env_checker.py      ←—— Check environment → diagnostic report
        │
   config/settings.py       ←—— Constants
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
