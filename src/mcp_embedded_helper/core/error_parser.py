"""交叉编译报错日志的结构化解析"""

import re


class BuildError:
    """单条编译错误的提取结果"""

    def __init__(self, file: str, line: int, error_type: str,
                 message: str, raw_line: str, severity: str = "ERROR"):
        self.file = file
        self.line = line
        self.error_type = error_type
        self.message = message
        self.raw_line = raw_line
        self.severity = severity

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "type": self.error_type,
            "severity": self.severity,
            "message": self.message,
            "raw": self.raw_line,
        }

    def __repr__(self):
        return f"BuildError({self.file}:{self.line} [{self.severity}] {self.error_type})"


class ErrorParser:
    """按行匹配编译输出，识别错误类型并提取文件名、行号、消息"""

    # 每种错误类型的严重程度
    # FATAL  → 编译无法进行
    # ERROR  → 编译失败，需修复
    # WARNING → 可编译通过，但建议修复
    _SEVERITY = {
        "toolchain_missing": "FATAL",
        "syntax_error": "ERROR",
        "header_missing": "ERROR",
        "linker_error": "ERROR",
        "arch_mismatch": "ERROR",
        "make_error": "ERROR",
        "warning": "WARNING",
    }

    # 每个 pattern 对应一种错误类型
    # 命名组: (?P<file>...) 文件名, (?P<line>...) 行号, (?P<msg>...) 消息
    _PATTERNS = [
        # -- header_missing --
        # drivers/led.c:3:22: fatal error: linux/gpio.h: No such file
        (
            re.compile(
                r"^(?P<file>[^\s:]+):(?P<line>\d+):\d+: "
                r"fatal error: (?P<msg>.*?No such file.*)$"
            ),
            "header_missing",
        ),
        # cc1: fatal error: include/types.h: No such file
        (
            re.compile(
                r"fatal error: (?P<file>[^\s:]+\.h):? (?P<msg>No such file.*)$"
            ),
            "header_missing",
        ),
        # -- linker_error --
        # led.c:(.text+0x42): undefined reference to 'gpio_request'
        (
            re.compile(
                r"(?P<file>[^\s:]+):\([^)]+\): undefined reference to "
                r"'(?P<msg>[^']+)'"
            ),
            "linker_error",
        ),
        # cannot find -lusb-1.0
        (
            re.compile(r"cannot find -(?P<msg>l\S+)"),
            "linker_error",
        ),
        # ld returned 1 exit status
        (
            re.compile(r"(?P<msg>ld returned \d+ exit status)"),
            "linker_error",
        ),
        # -- syntax_error --
        # led.c:42:5: error: expected ';' before '}' token
        (
            re.compile(
                r"^(?P<file>[^\s:]+):(?P<line>\d+):\d+: error: "
                r"(?P<msg>.*)$"
            ),
            "syntax_error",
        ),
        # led.c:20: error: 'GPIO_PIN' undeclared
        (
            re.compile(
                r"^(?P<file>[^\s:]+):(?P<line>\d+): error: "
                r"(?P<msg>.*)$"
            ),
            "syntax_error",
        ),
        # -- arch_mismatch --
        # skipping incompatible /usr/lib/libfoo.so
        (
            re.compile(r"skipping incompatible (?P<file>\S+)"),
            "arch_mismatch",
        ),
        # wrong architecture
        (
            re.compile(r"(?P<msg>.*wrong architecture.*)"),
            "arch_mismatch",
        ),
        # file format not recognized
        (
            re.compile(r"(?P<msg>.*file format not recognized.*)"),
            "arch_mismatch",
        ),
        # -- toolchain_missing --
        # make: arm-linux-gcc: Command not found
        (
            re.compile(
                r"(?P<file>\S*gcc\S*)?:? (?P<msg>[Cc]ommand not found)"
            ),
            "toolchain_missing",
        ),
        # arm-linux-gcc: No such file or directory
        (
            re.compile(
                r"(?P<file>\S*gcc\S*)?:? (?P<msg>No such file or directory)"
            ),
            "toolchain_missing",
        ),
        # -- make_error --
        # make[1]: *** [drivers/led.o] Error 1
        (
            re.compile(
                r"make\[\d*\]: \*\*\* \[(?P<file>[^\]]+)\] "
                r"(?P<msg>Error \d+)"
            ),
            "make_error",
        ),
        # -- warning --
        # led.c:55:3: warning: unused variable 'ret'
        (
            re.compile(
                r"^(?P<file>[^\s:]+):(?P<line>\d+):\d+: warning: "
                r"(?P<msg>.*)$"
            ),
            "warning",
        ),
    ]

    def parse(self, build_output: str) -> list:
        errors = []
        seen = set()  # 去重

        for line in build_output.split("\n"):
            line = line.strip()
            if not line:
                continue

            for pattern, error_type in self._PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue

                groups = match.groupdict()
                file = groups.get("file", "") or ""
                line_no = self._safe_int(groups.get("line", "0"))
                message = groups.get("msg", line)

                dedup_key = (file, line_no, error_type, message[:60])
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                severity = self._SEVERITY.get(error_type, "ERROR")
                error = BuildError(
                    file=file,
                    line=line_no,
                    error_type=error_type,
                    message=message.strip(),
                    raw_line=line,
                    severity=severity,
                )
                errors.append(error)
                break

        return [e.to_dict() for e in errors]

    @staticmethod
    def _safe_int(value: str) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def summary(self, errors: list) -> str:
        if not errors:
            return "未发现编译错误。"

        type_counts = {}
        for e in errors:
            t = e.get("type", "unknown") if isinstance(e, dict) else e.error_type
            type_counts[t] = type_counts.get(t, 0) + 1

        labels = {
            "header_missing": "头文件缺失",
            "linker_error": "链接错误",
            "syntax_error": "语法/声明错误",
            "arch_mismatch": "架构不匹配",
            "toolchain_missing": "工具链缺失",
            "make_error": "Makefile 错误",
            "warning": "编译警告",
        }
        lines = [f"共发现 {len(errors)} 条错误/警告:"]
        for t, c in sorted(type_counts.items()):
            label = labels.get(t, t)
            lines.append(f"  - {label}: {c} 条")
        return "\n".join(lines)
