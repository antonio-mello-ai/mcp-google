"""FastMCP server — tool registrations and entrypoint."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-google")

from mcp_google.tools import calendar, gmail  # noqa: E402, F401


def main() -> None:
    """Run the MCP server (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
