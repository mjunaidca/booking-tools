def lookup_property(properties: list[dict], property_id: str) -> dict:
    for prop in properties:
        if prop["property_id"] == property_id:
            return prop
    return {"success": False, "error": "Property not found", "code": "PROPERTY_NOT_FOUND"}


def register_get_property_details(mcp):
    from mcp.server.fastmcp import Context

    @mcp.tool(
        name="get_property_details",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_property_details(property_id: str, ctx: Context = None) -> dict:
        """Get complete details for a single property by ID. Returns full specifications, photo gallery, amenities, map link, and viewing instructions.

        Use after search_properties when the customer wants to know more about a specific listing. Returns all information needed for the customer to decide whether to schedule a viewing.
        """
        properties = ctx.request_context.lifespan_context["properties"]
        return lookup_property(properties, property_id)
