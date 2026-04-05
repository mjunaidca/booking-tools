import pytest
from property_catalog_mcp.models import SearchPropertiesInput
from property_catalog_mcp.tools.search_properties import filter_properties, build_search_response

SUMMARY_KEYS = {
    "property_id", "title", "location", "price", "price_formatted",
    "bedrooms", "bathrooms", "size_marla", "property_type", "purpose",
    "status", "owner_notes", "image_url", "listed_date",
}


class TestFilterProperties:
    def test_no_filters_returns_all(self, mock_properties):
        params = SearchPropertiesInput()
        result = filter_properties(mock_properties, params)
        assert len(result) == len(mock_properties)

    def test_filter_by_city(self, mock_properties):
        params = SearchPropertiesInput(city="Karachi")
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(p["location"]["city"] == "Karachi" for p in result)

    def test_filter_by_city_case_insensitive(self, mock_properties):
        params = SearchPropertiesInput(city="lahore")
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(p["location"]["city"].lower() == "lahore" for p in result)

    def test_filter_by_area_substring(self, mock_properties):
        params = SearchPropertiesInput(area="DHA")
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all("dha" in p["location"]["area"].lower() for p in result)

    def test_filter_by_area_case_insensitive(self, mock_properties):
        params = SearchPropertiesInput(area="dha phase 6")
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all("dha phase 6" in p["location"]["area"].lower() for p in result)

    def test_bedrooms_minimum_filter(self, mock_properties):
        params = SearchPropertiesInput(bedrooms=3)
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(p["bedrooms"] >= 3 for p in result)

    def test_budget_min_filter(self, mock_properties):
        params = SearchPropertiesInput(budget_min=10000000)
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(p["price"] >= 10000000 for p in result)

    def test_budget_max_filter(self, mock_properties):
        params = SearchPropertiesInput(budget_max=5000000)
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(p["price"] <= 5000000 for p in result)

    def test_budget_range_filter(self, mock_properties):
        params = SearchPropertiesInput(budget_min=5000000, budget_max=15000000)
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(5000000 <= p["price"] <= 15000000 for p in result)

    def test_property_type_filter(self, mock_properties):
        params = SearchPropertiesInput(property_type="apartment")
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(p["property_type"] == "apartment" for p in result)

    def test_purpose_filter(self, mock_properties):
        params = SearchPropertiesInput(purpose="rent")
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(p["purpose"] == "rent" for p in result)

    def test_size_range_filter(self, mock_properties):
        params = SearchPropertiesInput(size_min=5, size_max=10)
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        assert all(5 <= p["size_marla"] <= 10 for p in result)

    def test_combined_filters(self, mock_properties):
        params = SearchPropertiesInput(city="Lahore", bedrooms=2, budget_max=10000000)
        result = filter_properties(mock_properties, params)
        assert len(result) > 0
        for p in result:
            assert p["location"]["city"].lower() == "lahore"
            assert p["bedrooms"] >= 2
            assert p["price"] <= 10000000

    def test_no_matches_returns_empty(self, mock_properties):
        params = SearchPropertiesInput(city="Islamabad")
        result = filter_properties(mock_properties, params)
        assert result == []


class TestBuildSearchResponse:
    def test_pagination_default(self, mock_properties):
        params = SearchPropertiesInput(limit=3, offset=0)
        filtered = mock_properties  # all of them
        response = build_search_response(filtered, params)
        assert len(response["properties"]) == 3
        assert response["total"] == len(mock_properties)
        assert response["has_more"] is True
        assert response["next_offset"] == 3

    def test_pagination_offset(self, mock_properties):
        params = SearchPropertiesInput(limit=3, offset=3)
        response = build_search_response(mock_properties, params)
        assert len(response["properties"]) == 3
        assert response["total"] == len(mock_properties)
        assert response["has_more"] is True

    def test_pagination_last_page(self, mock_properties):
        total = len(mock_properties)
        params = SearchPropertiesInput(limit=total, offset=0)
        response = build_search_response(mock_properties, params)
        assert len(response["properties"]) == total
        assert response["has_more"] is False
        assert response["next_offset"] is None

    def test_pagination_beyond_results(self, mock_properties):
        params = SearchPropertiesInput(limit=10, offset=100)
        response = build_search_response(mock_properties, params)
        assert len(response["properties"]) == 0
        assert response["total"] == len(mock_properties)
        assert response["has_more"] is False

    def test_empty_results(self):
        params = SearchPropertiesInput()
        response = build_search_response([], params)
        assert response["properties"] == []
        assert response["total"] == 0
        assert response["has_more"] is False
        assert response["next_offset"] is None

    def test_summary_has_correct_keys(self, mock_properties):
        params = SearchPropertiesInput(limit=1)
        response = build_search_response(mock_properties, params)
        prop = response["properties"][0]
        assert set(prop.keys()) == SUMMARY_KEYS

    def test_summary_excludes_detail_fields(self, mock_properties):
        params = SearchPropertiesInput(limit=1)
        response = build_search_response(mock_properties, params)
        prop = response["properties"][0]
        for key in ["description", "features", "amenities", "photos", "viewing_instructions"]:
            assert key not in prop
