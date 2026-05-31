import os

from core.error_parser import ErrorParser
from core.env_checker import EnvChecker
from core.context_gatherer import ContextGatherer
from core.build_runner import BuildRunner


def register_tools(mcp):

    @mcp.tool()
    def analyze_build_error(log_text: str, project_dir: str = ".") -> str:
        """分析交叉编译报错日志，自动收集错误位置的源码上下文。

        log_text: 编译报错文本 或 日志文件路径
        project_dir: 项目根目录（用于定位源文件），默认当前目录
        """
        text = _resolve_input(log_text)
        return _analyze(text, project_dir)

    @mcp.tool()
    def run_build_and_analyze(target: str = "", extra_args: str = "",
                               project_dir: str = ".",
                               timeout: int = 120) -> str:
        """执行 make 编译，自动捕获并分析编译输出。

        target: make 目标（如 all, clean, modules），默认使用 Makefile 默认目标
        extra_args: 额外 make 参数（如 "ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-"）
        project_dir: 项目根目录，默认当前目录
        timeout: 构建超时秒数，默认 120
        """
        runner = BuildRunner(project_dir)
        result = runner.run(target=target, extra_args=extra_args,
                           timeout=timeout)

        if result.exit_code == -1:
            return f"构建执行失败:\n{result.stderr}"

        if not result.output:
            return f"构建完成（无输出）\n命令: {result.command}\n退出码: {result.exit_code}"

        return _analyze(result.output, project_dir)

    @mcp.tool()
    def check_cross_env(project_dir: str = ".") -> str:
        """一键诊断交叉编译环境。

        检查 CROSS_COMPILE、ARCH、CC 环境变量，交叉编译器是否可用，
        make 版本，以及当前目录是否有 Makefile。
        """
        checker = EnvChecker(project_dir)
        results = checker.run_all()
        return checker.summary(results)


def _analyze(text: str, project_dir: str) -> str:
    parser = ErrorParser()
    errors = parser.parse(text)

    if not errors:
        return "未检测到编译错误或警告。"

    gatherer = ContextGatherer(project_dir)
    contexts = gatherer.gather(errors)

    lines = [parser.summary(errors), "", _format_errors(errors)]
    if contexts:
        lines.append("")
        lines.append(_format_contexts(contexts))
    return "\n".join(lines)


def _resolve_input(log_text: str) -> str:
    if len(log_text) < 512 and os.path.isfile(log_text.strip()):
        with open(log_text.strip(), "r") as f:
            return f.read()
    return log_text


def _format_errors(errors: list) -> str:
    lines = []
    for i, e in enumerate(errors, 1):
        marker = {"FATAL": "X", "ERROR": "E", "WARNING": "W"}.get(
            e.get("severity", "ERROR"), " ")
        lines.append(
            f"  [{i}] [{e['severity'][:1]}] {marker} "
            f"{e['file']}:{e['line']}  {e['message']}"
        )
    return "\n".join(lines)


def _format_contexts(contexts: dict) -> str:
    lines = ["--- 源码上下文 ---"]
    for file_path, info in contexts.items():
        lines.append(f"\n  {file_path}:")
        for snippet in info["snippets"]:
            lines.append(snippet)
            lines.append("")
    return "\n".join(lines)
