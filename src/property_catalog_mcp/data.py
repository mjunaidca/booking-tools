import json
from pathlib import Path


def load_properties_from_json() -> list[dict]:
    path = Path(__file__).parent / "mock_data" / "properties.json"
    with open(path) as f:
        return json.load(f)
