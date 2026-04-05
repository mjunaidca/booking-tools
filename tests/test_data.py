from property_catalog_mcp.data import load_properties_from_json


REQUIRED_KEYS = {
    "property_id", "title", "description", "location", "price", "price_formatted",
    "bedrooms", "bathrooms", "size_marla", "property_type", "purpose", "status",
    "features", "amenities", "photos", "owner_notes", "listed_date",
    "viewing_instructions", "image_url",
}

LOCATION_KEYS = {"city", "area", "address"}


class TestLoadProperties:
    def test_returns_list(self):
        properties = load_properties_from_json()
        assert isinstance(properties, list)
        assert len(properties) > 0

    def test_all_have_required_keys(self):
        properties = load_properties_from_json()
        for prop in properties:
            missing = REQUIRED_KEYS - set(prop.keys())
            assert not missing, f"Property {prop.get('property_id', '?')} missing keys: {missing}"

    def test_location_has_required_keys(self):
        properties = load_properties_from_json()
        for prop in properties:
            loc = prop["location"]
            missing = LOCATION_KEYS - set(loc.keys())
            assert not missing, f"Property {prop['property_id']} location missing: {missing}"

    def test_unique_ids(self):
        properties = load_properties_from_json()
        ids = [p["property_id"] for p in properties]
        assert len(ids) == len(set(ids)), "Duplicate property IDs found"

    def test_valid_property_types(self):
        valid = {"house", "apartment", "plot", "commercial", "shop", "office"}
        properties = load_properties_from_json()
        for prop in properties:
            assert prop["property_type"] in valid, f"{prop['property_id']} has invalid type: {prop['property_type']}"

    def test_valid_purposes(self):
        valid = {"buy", "rent"}
        properties = load_properties_from_json()
        for prop in properties:
            assert prop["purpose"] in valid, f"{prop['property_id']} has invalid purpose: {prop['purpose']}"

    def test_valid_statuses(self):
        valid = {"available", "under_offer", "sold"}
        properties = load_properties_from_json()
        for prop in properties:
            assert prop["status"] in valid, f"{prop['property_id']} has invalid status: {prop['status']}"

    def test_has_mix_of_cities(self):
        properties = load_properties_from_json()
        cities = {p["location"]["city"] for p in properties}
        assert len(cities) >= 2, "Need properties in at least 2 cities"

    def test_has_mix_of_types(self):
        properties = load_properties_from_json()
        types = {p["property_type"] for p in properties}
        assert len(types) >= 3, "Need at least 3 property types"
