"""根据报错位置读取源文件上下文"""

import os
from typing import Optional


class ContextGatherer:

    def __init__(self, project_root: str = ".", context_lines: int = 8):
        self.project_root = os.path.abspath(project_root)
        self.context_lines = context_lines

    def gather(self, errors: list) -> dict:
        """为每条错误收集对应源文件的上下文代码。

        返回 {file_path: {"content": str, "errors": [行号列表]}}
        每个源码文件只读一次，多个错误指向同一个文件时合并。
        """
        # 按文件分组
        file_errors: dict = {}
        for e in errors:
            f = e.get("file", "")
            if not f:
                continue
            full_path = self._resolve_path(f)
            if not full_path:
                continue
            if full_path not in file_errors:
                file_errors[full_path] = []
            file_errors[full_path].append(e.get("line", 0))

        result = {}
        for full_path, lines in file_errors.items():
            snippet = self._read_snippet(full_path, lines)
            if snippet:
                result[full_path] = snippet
        return result

    def _resolve_path(self, file_path: str) -> Optional[str]:
        """在项目根目录下查找源文件"""
        full = os.path.join(self.project_root, file_path)
        if os.path.isfile(full):
            return full
        # 文件名可能不带路径前缀，递归搜
        basename = os.path.basename(file_path)
        for root, dirs, files in os.walk(self.project_root):
            # 跳过隐藏目录和构建产物
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "build"]
            if basename in files:
                return os.path.join(root, basename)
        return None

    def _read_snippet(self, file_path: str, error_lines: list) -> Optional[dict]:
        """读取文件并截取每个错误行附近的内容"""
        if not os.path.isfile(file_path):
            return None

        try:
            with open(file_path, "r") as f:
                all_lines = f.readlines()
        except (IOError, OSError):
            return None

        total = len(all_lines)
        n = self.context_lines
        parts = []

        for ln in sorted(set(error_lines)):
            if ln <= 0 or ln > total:
                continue
            start = max(0, ln - n - 1)
            end = min(total, ln + n)
            chunk = []
            for i in range(start, end):
                marker = ">>>" if i == ln - 1 else "   "
                chunk.append(f"{marker} {i + 1:4d}  {all_lines[i].rstrip()}")
            parts.append("\n".join(chunk))

        if not parts:
            return None

        return {
            "file": file_path,
            "snippets": parts,
            "total_lines": total,
        }
