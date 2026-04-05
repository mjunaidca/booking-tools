from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from property_catalog_mcp.data import load_properties_from_json
from property_catalog_mcp.tools.search_properties import register_search_properties
from property_catalog_mcp.tools.get_property_details import register_get_property_details


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    properties = load_properties_from_json()
    yield {"properties": properties}


mcp = FastMCP(
    "property_catalog_mcp",
    stateless_http=True,
    json_response=True,
    lifespan=app_lifespan,
)

register_search_properties(mcp)
register_get_property_details(mcp)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
