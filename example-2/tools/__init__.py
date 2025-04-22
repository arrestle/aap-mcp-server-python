from tools.loadavg import get_load_avg


def register_tools(mcp):
    mcp.tool(name="get_load_avg", description="Retrieve 3-min system load avg")(get_load_avg)