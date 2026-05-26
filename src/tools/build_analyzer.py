import os

from core.error_parser import ErrorParser
from core.env_checker import EnvChecker


def register_tools(mcp):

    @mcp.tool()
    def analyze_build_error(log_text: str) -> str:
        """分析交叉编译报错日志。

        参数 log_text 可以是:
        - 直接粘贴的编译报错文本
        - 报错日志文件的路径（如 /home/user/build.log）

        返回结构化的错误分析，包含每条错误的文件名、行号、类型和严重级别。
        """
        text = _resolve_input(log_text)
        parser = ErrorParser()
        errors = parser.parse(text)

        if not errors:
            return "未检测到编译错误或警告。"

        lines = [parser.summary(errors), "", _format_errors(errors)]
        return "\n".join(lines)

    @mcp.tool()
    def check_cross_env(project_dir: str = ".") -> str:
        """一键诊断交叉编译环境。

        检查 CROSS_COMPILE、ARCH、CC 环境变量，交叉编译器是否可用，
        make 版本，以及当前目录是否有 Makefile。
        """
        checker = EnvChecker(project_dir)
        results = checker.run_all()
        return checker.summary(results)


def _resolve_input(log_text: str) -> str:
    if len(log_text) < 512 and os.path.isfile(log_text.strip()):
        with open(log_text.strip(), "r") as f:
            return f.read()
    return log_text


def _format_errors(errors: list) -> str:
    lines = []
    for i, e in enumerate(errors, 1):
        marker = {"FATAL": "🔴", "ERROR": "🟡", "WARNING": "⚪"}.get(
            e.get("severity", "ERROR"), "  ")
        lines.append(
            f"  [{i}] [{e['severity']:7s}] {marker} "
            f"{e['file']}:{e['line']}  {e['message']}"
        )
    return "\n".join(lines)
