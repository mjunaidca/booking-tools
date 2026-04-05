import pytest
from property_catalog_mcp.data import load_properties_from_json


@pytest.fixture
def mock_properties():
    return load_properties_from_json()
