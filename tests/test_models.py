import pytest
from pydantic import ValidationError
from property_catalog_mcp.models import (
    PropertyType,
    Purpose,
    SearchPropertiesInput,
    GetPropertyDetailsInput,
)


class TestPropertyTypeEnum:
    def test_valid_values(self):
        for val in ["house", "apartment", "plot", "commercial", "shop", "office"]:
            assert PropertyType(val).value == val

    def test_invalid_value(self):
        with pytest.raises(ValueError):
            PropertyType("villa")


class TestPurposeEnum:
    def test_valid_values(self):
        assert Purpose("buy").value == "buy"
        assert Purpose("rent").value == "rent"

    def test_invalid_value(self):
        with pytest.raises(ValueError):
            Purpose("lease")


class TestSearchPropertiesInput:
    def test_all_empty_is_valid(self):
        params = SearchPropertiesInput()
        assert params.city is None
        assert params.limit == 10
        assert params.offset == 0

    def test_all_fields_provided(self):
        params = SearchPropertiesInput(
            city="Lahore",
            area="DHA Phase 6",
            bedrooms=2,
            budget_min=5000000,
            budget_max=10000000,
            property_type=PropertyType.HOUSE,
            purpose=Purpose.BUY,
            size_min=5,
            size_max=10,
            limit=5,
            offset=10,
        )
        assert params.city == "Lahore"
        assert params.bedrooms == 2
        assert params.property_type == PropertyType.HOUSE

    def test_rejects_budget_max_less_than_min(self):
        with pytest.raises(ValidationError, match="budget_max must be >= budget_min"):
            SearchPropertiesInput(budget_min=10000000, budget_max=5000000)

    def test_rejects_size_max_less_than_min(self):
        with pytest.raises(ValidationError, match="size_max must be >= size_min"):
            SearchPropertiesInput(size_min=10, size_max=5)

    def test_budget_max_without_min_is_valid(self):
        params = SearchPropertiesInput(budget_max=10000000)
        assert params.budget_max == 10000000
        assert params.budget_min is None

    def test_size_max_without_min_is_valid(self):
        params = SearchPropertiesInput(size_max=10)
        assert params.size_max == 10

    def test_limit_bounds(self):
        with pytest.raises(ValidationError):
            SearchPropertiesInput(limit=0)
        with pytest.raises(ValidationError):
            SearchPropertiesInput(limit=21)

    def test_limit_valid_bounds(self):
        assert SearchPropertiesInput(limit=1).limit == 1
        assert SearchPropertiesInput(limit=20).limit == 20

    def test_negative_offset_rejected(self):
        with pytest.raises(ValidationError):
            SearchPropertiesInput(offset=-1)

    def test_strips_whitespace(self):
        params = SearchPropertiesInput(city="  Lahore  ", area="  DHA Phase 6  ")
        assert params.city == "Lahore"
        assert params.area == "DHA Phase 6"

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            SearchPropertiesInput(unknown_field="value")

    def test_bedrooms_bounds(self):
        with pytest.raises(ValidationError):
            SearchPropertiesInput(bedrooms=0)
        with pytest.raises(ValidationError):
            SearchPropertiesInput(bedrooms=11)


class TestGetPropertyDetailsInput:
    def test_valid_id(self):
        params = GetPropertyDetailsInput(property_id="prop_001")
        assert params.property_id == "prop_001"

    def test_rejects_empty_string(self):
        with pytest.raises(ValidationError):
            GetPropertyDetailsInput(property_id="")

    def test_strips_whitespace(self):
        params = GetPropertyDetailsInput(property_id="  prop_001  ")
        assert params.property_id == "prop_001"

    def test_rejects_missing_id(self):
        with pytest.raises(ValidationError):
            GetPropertyDetailsInput()
