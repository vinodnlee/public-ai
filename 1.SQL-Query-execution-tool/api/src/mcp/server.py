"""
Expose this application as an MCP server with a single tool: query_database.

MCP clients can call query_database(question) to run the DeepAgent and get
the final answer as a string.
"""

from fastmcp import FastMCP

from src.mcp.run_agent import run_agent_and_collect

MCP_NAME = "DeepAgent SQL"


def _create_mcp() -> FastMCP:
    mcp = FastMCP(MCP_NAME)

    @mcp.tool
    async def query_database(question: str) -> str:
        """
        Answer a natural language question about the connected database.

        Runs the SQL agent: it may generate and execute SQL, then returns
        the final answer in plain text. Use this for analytics, counts,
        and exploratory questions.
        """
        return await run_agent_and_collect(question)

    return mcp


def get_mcp_asgi_app(path: str = "/"):
    """
    Return the ASGI app for the MCP server, to be mounted on the FastAPI app.

    Use path="/" when mounting at e.g. /mcp so the MCP endpoint is at /mcp/.
    The caller must combine the returned app's lifespan with the FastAPI lifespan.
    """
    mcp = _create_mcp()
    return mcp.http_app(path=path)
