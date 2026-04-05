# Domain 1: Property Catalog — Tool Schemas

## MCP Server: `property_catalog_mcp`

---

## Tool 1: `search_properties`

### Description (agent prompt)

```
Search available properties by location, budget, size, and type. Returns a summary
list of matching properties — enough to present options to the customer.

Use get_property_details for full information (photos, map, amenities) on a specific property.

Results are sorted by relevance and paginated (default 10 per call). If no properties
match, returns an empty list — suggest the customer broaden their criteria.

bedrooms is a minimum filter: bedrooms=2 returns properties with 2 or more bedrooms.
size_min/size_max are in marla (1 kanal = 20 marla).
Prices are in PKR.
```

### Annotations

```python
readOnlyHint = True
destructiveHint = False
idempotentHint = True
openWorldHint = True
```

### Input Schema

| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| `city` | string | no | — | min 1, max 50 | City name (e.g. "Lahore", "Karachi", "Islamabad") |
| `area` | string | no | — | min 1, max 100 | Locality or society (e.g. "DHA Phase 6", "Bahria Town", "Gulberg"). Free text, fuzzy-matched. |
| `bedrooms` | int | no | — | ge 1, le 10 | Minimum number of bedrooms. `bedrooms=2` returns 2, 3, 4+ BR properties. |
| `budget_min` | int | no | — | ge 0 | Minimum price in PKR. |
| `budget_max` | int | no | — | ge 0 | Maximum price in PKR. Agent converts customer language: "85 lac" → 8500000, "1.2 crore" → 12000000. |
| `property_type` | enum | no | — | `house`, `apartment`, `plot`, `commercial`, `shop`, `office` | Type of property. |
| `purpose` | enum | no | — | `buy`, `rent` | Whether customer wants to buy or rent. |
| `size_min` | int | no | — | ge 1 | Minimum size in marla. |
| `size_max` | int | no | — | ge 1 | Maximum size in marla. |
| `limit` | int | no | 10 | ge 1, le 20 | Number of results to return. |
| `offset` | int | no | 0 | ge 0 | Pagination offset. |

### Output Schema

```json
{
    "properties": [
        {
            "property_id": "prop_123",
            "title": "5 Marla House in DHA Phase 6",
            "location": {
                "city": "Lahore",
                "area": "DHA Phase 6",
                "address": "Street 12, Block D"
            },
            "price": 8500000,
            "price_formatted": "85 Lac",
            "bedrooms": 2,
            "bathrooms": 2,
            "size_marla": 5,
            "property_type": "house",
            "purpose": "buy",
            "status": "available | under_offer | sold",
            "owner_notes": "Owner prefers evening viewings",
            "image_url": "https://...",
            "listed_date": "2026-03-15"
        }
    ],
    "total": 24,
    "has_more": true,
    "next_offset": 10
}
```

### Field notes

- `price_formatted` — human-readable price so the agent can say "85 Lac" directly without conversion
- `status` — agent can filter in conversation: "3 of 4 are available for viewing"
- `owner_notes` — included in search results when available, so the agent has scheduling context early (e.g. "owner prefers evenings")
- `image_url` — single thumbnail, not the full gallery
- `address` — enough for customer to recognize the area, not full directions

---

## Tool 2: `get_property_details`

### Description (agent prompt)

```
Get complete details for a single property by ID. Returns full specifications, photo
gallery, amenities, map link, and viewing instructions.

Use after search_properties when the customer wants to know more about a specific listing.
Returns all information needed for the customer to decide whether to schedule a viewing.
```

### Annotations

```python
readOnlyHint = True
destructiveHint = False
idempotentHint = True
openWorldHint = True
```

### Input Schema

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `property_id` | string | yes | min 1 | Property ID from search_properties results. |

### Output Schema

```json
{
    "property_id": "prop_123",
    "title": "5 Marla House in DHA Phase 6",
    "description": "Recently renovated 2-bedroom house with modern kitchen and spacious drawing room. Corner plot with car porch for 2 cars.",
    "location": {
        "city": "Lahore",
        "area": "DHA Phase 6",
        "block": "D",
        "street": "Street 12",
        "address": "House 45, Street 12, Block D, DHA Phase 6, Lahore",
        "map_url": "https://maps.google.com/..."
    },
    "price": 8500000,
    "price_formatted": "85 Lac",
    "bedrooms": 2,
    "bathrooms": 2,
    "size_marla": 5,
    "property_type": "house",
    "purpose": "buy",
    "status": "available",
    "features": [
        "Newly renovated",
        "Corner plot",
        "Servant quarter",
        "Car porch for 2 cars"
    ],
    "amenities": [
        "Gas",
        "Electricity (no load-shedding area)",
        "Sui gas",
        "Broadband available"
    ],
    "photos": [
        {"url": "https://...", "caption": "Front view"},
        {"url": "https://...", "caption": "Drawing room"},
        {"url": "https://...", "caption": "Kitchen"}
    ],
    "owner_notes": "Owner prefers evening viewings after 4pm",
    "listed_date": "2026-03-15",
    "viewing_instructions": "Enter from main gate, house is 3rd on the left"
}
```

### Field notes

- `features` — selling points (corner plot, renovated, servant quarter)
- `amenities` — utilities and infrastructure (gas, electricity, broadband)
- `photos` with captions — agent can say "I can show you photos of the drawing room and kitchen"
- `owner_notes` — scheduling context for the agent (not shared with customer directly)
- `viewing_instructions` — agent shares when confirming a booking
- `map_url` — agent shares for directions, no separate tool needed
- `description` — free-text property description the agent can paraphrase

---

## Error Format

Both tools use the same error structure:

```json
{
    "success": false,
    "error": "Property not found",
    "code": "PROPERTY_NOT_FOUND"
}
```

Error codes:

| Code | When |
|---|---|
| `PROPERTY_NOT_FOUND` | `get_property_details` with invalid ID |
| `INVALID_FILTERS` | `search_properties` with conflicting filters (e.g. budget_min > budget_max) |
| `SERVICE_UNAVAILABLE` | Backend database is down |
