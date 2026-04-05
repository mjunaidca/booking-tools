import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


SERVER_URL = "http://localhost:8000/mcp"


@pytest.fixture
async def client():
    async with streamablehttp_client(SERVER_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


@pytest.mark.integration
class TestServerIntegration:
    async def test_list_tools(self, client):
        result = await client.list_tools()
        tool_names = {t.name for t in result.tools}
        assert "search_properties" in tool_names
        assert "get_property_details" in tool_names

    async def test_search_properties_call(self, client):
        result = await client.call_tool("search_properties", {"city": "Lahore"})
        assert len(result.content) > 0

    async def test_search_properties_with_filters(self, client):
        result = await client.call_tool("search_properties", {"city": "Lahore", "bedrooms": 2, "budget_max": 10000000})
        assert len(result.content) > 0

    async def test_get_property_details_call(self, client):
        result = await client.call_tool("get_property_details", {"property_id": "prop_001"})
        assert len(result.content) > 0

    async def test_get_property_details_not_found(self, client):
        result = await client.call_tool("get_property_details", {"property_id": "nonexistent"})
        assert len(result.content) > 0
