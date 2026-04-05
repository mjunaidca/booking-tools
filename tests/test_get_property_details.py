import pytest
from property_catalog_mcp.tools.get_property_details import lookup_property


DETAIL_KEYS = {
    "property_id", "title", "description", "location", "price", "price_formatted",
    "bedrooms", "bathrooms", "size_marla", "property_type", "purpose", "status",
    "features", "amenities", "photos", "owner_notes", "listed_date",
    "viewing_instructions", "image_url",
}


class TestLookupProperty:
    def test_valid_id_returns_property(self, mock_properties):
        result = lookup_property(mock_properties, "prop_001")
        assert result["property_id"] == "prop_001"

    def test_returns_all_detail_keys(self, mock_properties):
        result = lookup_property(mock_properties, "prop_001")
        assert set(result.keys()) >= DETAIL_KEYS

    def test_includes_photos(self, mock_properties):
        result = lookup_property(mock_properties, "prop_001")
        assert isinstance(result["photos"], list)
        assert len(result["photos"]) > 0
        assert "url" in result["photos"][0]
        assert "caption" in result["photos"][0]

    def test_includes_features_and_amenities(self, mock_properties):
        result = lookup_property(mock_properties, "prop_001")
        assert isinstance(result["features"], list)
        assert isinstance(result["amenities"], list)

    def test_includes_map_url_in_location(self, mock_properties):
        result = lookup_property(mock_properties, "prop_001")
        assert "map_url" in result["location"]

    def test_invalid_id_returns_error(self, mock_properties):
        result = lookup_property(mock_properties, "nonexistent")
        assert result["success"] is False
        assert result["code"] == "PROPERTY_NOT_FOUND"

    def test_different_valid_ids(self, mock_properties):
        for pid in ["prop_002", "prop_009", "prop_012"]:
            result = lookup_property(mock_properties, pid)
            assert result["property_id"] == pid
