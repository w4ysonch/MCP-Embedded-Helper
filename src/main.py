from mcp.server.fastmcp import FastMCP
import os

from tools.build_analyzer import register_tools

mcp = FastMCP("Embedded-Dev-Helper")

register_tools(mcp)


@mcp.tool()
def list_files() -> str:
    """列出当前工程目录下的所有文件"""
    files = os.listdir(".")
    return "当前目录包含以下文件: " + ", ".join(files)


if __name__ == "__main__":
    mcp.run()
