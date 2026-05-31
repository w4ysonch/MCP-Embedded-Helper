import os
import shutil
import subprocess
from pathlib import Path

from ..config.settings import COMMON_TOOLCHAIN_PREFIXES, ENV_CROSS_COMPILE, ENV_ARCH, ENV_CC


class EnvCheckResult:
    """单条环境检查的结果"""

    def __init__(self, item: str, status: str, detail: str = "",
                 fix_hint: str = ""):
        self.item = item
        self.status = status   # OK, MISSING, ERROR
        self.detail = detail
        self.fix_hint = fix_hint

    def to_dict(self) -> dict:
        return {
            "item": self.item,
            "status": self.status,
            "detail": self.detail,
            "fix_hint": self.fix_hint,
        }


class EnvChecker:
    """一键诊断交叉编译环境"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).resolve()

    def run_all(self) -> list:
        checks = []
        checks.append(self._check_env_var(ENV_CROSS_COMPILE, "交叉编译器前缀"))
        checks.append(self._check_env_var(ENV_ARCH, "目标架构"))
        checks.append(self._check_env_var(ENV_CC, "C 编译器"))
        checks.append(self._check_toolchain())
        checks.append(self._check_make())
        checks.append(self._check_makefile())
        return checks

    def _check_env_var(self, var: str, label: str) -> EnvCheckResult:
        value = os.environ.get(var, "")
        if value:
            return EnvCheckResult(
                item=f"${var}",
                status="OK",
                detail=f"{label}: {value}",
            )
        return EnvCheckResult(
            item=f"${var}",
            status="MISSING",
            detail=f"{label} 未设置",
            fix_hint=f"export {var}=<路径>  或写入 ~/.bashrc",
        )

    def _check_toolchain(self) -> EnvCheckResult:
        cross = os.environ.get(ENV_CROSS_COMPILE, "")
        compiler = f"{cross}gcc" if cross else ""

        # 1. 先检查 CROSS_COMPILE 对应的编译器
        if compiler:
            found = shutil.which(compiler)
            if found:
                return EnvCheckResult(
                    item="交叉编译器",
                    status="OK",
                    detail=f"{compiler} → {found}",
                )
            return EnvCheckResult(
                item="交叉编译器",
                status="MISSING",
                detail=f"{compiler} 不在 PATH 中",
                fix_hint=f"检查 PATH 是否包含工具链的 bin 目录",
            )

        # 2. 没设 CROSS_COMPILE，扫描常见前缀
        found_any = []
        for prefix in COMMON_TOOLCHAIN_PREFIXES:
            c = f"{prefix}gcc"
            path = shutil.which(c)
            if path:
                found_any.append(f"{c} → {path}")

        if found_any:
            return EnvCheckResult(
                item="交叉编译器",
                status="OK",
                detail="\n".join(found_any),
            )

        return EnvCheckResult(
            item="交叉编译器",
            status="MISSING",
            detail="未找到任何交叉编译器",
            fix_hint="安装工具链后设置 CROSS_COMPILE 和 PATH 环境变量",
        )

    def _check_make(self) -> EnvCheckResult:
        path = shutil.which("make")
        if not path:
            return EnvCheckResult(
                item="make",
                status="MISSING",
                detail="未安装 make",
                fix_hint="sudo apt install make",
            )

        try:
            result = subprocess.run(
                ["make", "--version"], capture_output=True, text=True, timeout=5
            )
            version_line = result.stdout.split("\n")[0] if result.stdout else ""
            return EnvCheckResult(
                item="make",
                status="OK",
                detail=f"{path}  {version_line}",
            )
        except Exception as e:
            return EnvCheckResult(
                item="make",
                status="ERROR",
                detail=f"运行 make --version 失败: {e}",
            )

    def _check_makefile(self) -> EnvCheckResult:
        makefile = self.project_dir / "Makefile"
        if makefile.exists():
            return EnvCheckResult(
                item="Makefile",
                status="OK",
                detail=f"存在: {makefile}",
            )
        return EnvCheckResult(
            item="Makefile",
            status="MISSING",
            detail="当前目录未找到 Makefile",
            fix_hint="在项目根目录创建 Makefile 或切换到正确的构建目录",
        )

    def summary(self, results: list) -> str:
        status_order = {"FATAL": 0, "MISSING": 1, "ERROR": 2, "OK": 3}
        sorted_results = sorted(
            results, key=lambda r: status_order.get(r.status, 99)
        )

        lines = ["环境诊断结果:"]
        for r in sorted_results:
            if r.status == "OK":
                lines.append(f"  [OK]      {r.item} — {r.detail}")
            elif r.status == "MISSING":
                lines.append(f"  [MISSING] {r.item} — {r.detail}")
                if r.fix_hint:
                    lines.append(f"            → {r.fix_hint}")
            else:
                lines.append(f"  [ERROR]   {r.item} — {r.detail}")
                if r.fix_hint:
                    lines.append(f"            → {r.fix_hint}")
        return "\n".join(lines)
