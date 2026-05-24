# src/main.py
from mcp.server.fastmcp import FastMCP
import os

# 初始化 MCP 服务器
mcp = FastMCP("Embedded-Dev-Helper")

@mcp.tool()
def list_files() -> str:
    """列出当前工程目录下的所有文件，方便大模型了解项目结构"""
    files = os.listdir(".")
    return "当前目录包含以下文件: " + ", ".join(files)

if __name__ == "__main__":
    mcp.run()