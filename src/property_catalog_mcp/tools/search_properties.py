from property_catalog_mcp.models import SearchPropertiesInput


SUMMARY_FIELDS = [
    "property_id", "title", "location", "price", "price_formatted",
    "bedrooms", "bathrooms", "size_marla", "property_type", "purpose",
    "status", "owner_notes", "image_url", "listed_date",
]


def filter_properties(properties: list[dict], params: SearchPropertiesInput) -> list[dict]:
    result = properties

    if params.city is not None:
        result = [p for p in result if p["location"]["city"].lower() == params.city.lower()]

    if params.area is not None:
        area_lower = params.area.lower()
        result = [p for p in result if area_lower in p["location"]["area"].lower()]

    if params.bedrooms is not None:
        result = [p for p in result if p["bedrooms"] >= params.bedrooms]

    if params.budget_min is not None:
        result = [p for p in result if p["price"] >= params.budget_min]

    if params.budget_max is not None:
        result = [p for p in result if p["price"] <= params.budget_max]

    if params.property_type is not None:
        result = [p for p in result if p["property_type"] == params.property_type.value]

    if params.purpose is not None:
        result = [p for p in result if p["purpose"] == params.purpose.value]

    if params.size_min is not None:
        result = [p for p in result if p["size_marla"] >= params.size_min]

    if params.size_max is not None:
        result = [p for p in result if p["size_marla"] <= params.size_max]

    return result


def _to_summary(prop: dict) -> dict:
    return {key: prop[key] for key in SUMMARY_FIELDS}


def build_search_response(filtered: list[dict], params: SearchPropertiesInput) -> dict:
    total = len(filtered)
    page = filtered[params.offset : params.offset + params.limit]
    has_more = params.offset + params.limit < total

    return {
        "properties": [_to_summary(p) for p in page],
        "total": total,
        "has_more": has_more,
        "next_offset": params.offset + params.limit if has_more else None,
    }


def register_search_properties(mcp):
    from mcp.server.fastmcp import Context

    @mcp.tool(
        name="search_properties",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def search_properties(
        city: str | None = None,
        area: str | None = None,
        bedrooms: int | None = None,
        budget_min: int | None = None,
        budget_max: int | None = None,
        property_type: str | None = None,
        purpose: str | None = None,
        size_min: int | None = None,
        size_max: int | None = None,
        limit: int = 10,
        offset: int = 0,
        ctx: Context = None,
    ) -> dict:
        """Search available properties by location, budget, size, and type. Returns a summary list of matching properties — enough to present options to the customer.

        Use get_property_details for full information (photos, map, amenities) on a specific property.

        Results are sorted by relevance and paginated (default 10 per call). If no properties match, returns an empty list — suggest the customer broaden their criteria.

        bedrooms is a minimum filter: bedrooms=2 returns properties with 2 or more bedrooms.
        size_min/size_max are in marla (1 kanal = 20 marla).
        Prices are in PKR.
        """
        try:
            params = SearchPropertiesInput(
                city=city,
                area=area,
                bedrooms=bedrooms,
                budget_min=budget_min,
                budget_max=budget_max,
                property_type=property_type,
                purpose=purpose,
                size_min=size_min,
                size_max=size_max,
                limit=limit,
                offset=offset,
            )
        except Exception as e:
            return {"success": False, "error": str(e), "code": "INVALID_FILTERS"}

        properties = ctx.request_context.lifespan_context["properties"]
        filtered = filter_properties(properties, params)
        return build_search_response(filtered, params)
