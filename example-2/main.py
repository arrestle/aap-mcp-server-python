import argparse
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from tools import register_tools
from api import app as fastapi_app

mcp = FastMCP(name="hybrid_mcp")
register_tools(mcp)  # dynamically registers tools

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true")
    args = parser.parse_args()

    # Note that you can't run both uvicorn and mcp at the same time
    # because they both use asyncio. If you need both run them in separate processes.
    if args.http:
        import uvicorn
        uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

    else:
        mcp.run(transport="stdio")
