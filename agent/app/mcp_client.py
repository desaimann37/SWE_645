# Thin wrapper around langchain-mcp-adapters that connects to our FastMCP
# backend and returns LangChain-compatible Tool objects.
import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

_client: MultiServerMCPClient | None = None
_tools: List[BaseTool] | None = None


def _build_client() -> MultiServerMCPClient:
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/")
    return MultiServerMCPClient(
        {
            "survey": {
                "url": mcp_url,
                "transport": "streamable_http",
            }
        }
    )


async def get_mcp_tools() -> List[BaseTool]:
    """Load MCP tools once and cache them for the process lifetime."""
    global _client, _tools
    if _tools is None:
        _client = _build_client()
        _tools = await _client.get_tools()
    return _tools


def get_tool_by_name(tools: List[BaseTool], name: str) -> BaseTool:
    for t in tools:
        if t.name == name:
            return t
    raise ValueError(f"Tool '{name}' not found. Available: {[t.name for t in tools]}")