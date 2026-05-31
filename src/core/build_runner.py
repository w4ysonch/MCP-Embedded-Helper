import subprocess
import os


class BuildResult:

    def __init__(self, exit_code: int, stdout: str, stderr: str,
                 command: str, cwd: str):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.command = command
        self.cwd = cwd

    @property
    def failed(self) -> bool:
        return self.exit_code != 0

    @property
    def output(self) -> str:
        """合并 stdout + stderr，方便直接喂给 error_parser"""
        parts = []
        if self.stdout.strip():
            parts.append(self.stdout.strip())
        if self.stderr.strip():
            parts.append(self.stderr.strip())
        return "\n".join(parts)

    def to_dict(self) -> dict:
        return {
            "exit_code": self.exit_code,
            "failed": self.failed,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "command": self.command,
            "cwd": self.cwd,
        }


class BuildRunner:
    """在指定目录执行 make 或其他编译命令并捕获输出"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = os.path.abspath(project_dir)

    def run(self, target: str = "", extra_args: str = "",
            timeout: int = 120) -> BuildResult:
        """执行 make [target]，返回 BuildResult。

        target: make 目标（如 all, clean, modules, 默认空=默认目标）
        extra_args: 额外参数（如 ARCH=arm CROSS_COMPILE=xxx）
        timeout: 超时秒数
        """
        cmd_parts = ["make"]
        if extra_args:
            cmd_parts.extend(extra_args.split())
        if target:
            cmd_parts.append(target)
        cmd_str = " ".join(cmd_parts)

        try:
            result = subprocess.run(
                cmd_parts,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return BuildResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=cmd_str,
                cwd=self.project_dir,
            )
        except subprocess.TimeoutExpired:
            return BuildResult(
                exit_code=-1,
                stdout="",
                stderr=f"构建超时（{timeout}s）: {cmd_str}",
                command=cmd_str,
                cwd=self.project_dir,
            )
        except FileNotFoundError:
            return BuildResult(
                exit_code=-1,
                stdout="",
                stderr=f"未找到 make 命令，请确认已安装",
                command=cmd_str,
                cwd=self.project_dir,
            )
