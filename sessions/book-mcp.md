# Session Log: Building the Property Catalog MCP Server

**Date:** 2026-04-05

---

## Phase 1: Simulation & Tool Discovery

Started by simulating a full customer-agent conversation — a customer looking for 2BR in DHA Phase 6, Lahore. The simulation surfaced **15 potential tools** across search, calendar, communication, knowledge, CRM, and escalation categories.

## Phase 2: Tool Reduction (15 → 5)

Three key decisions drove the cut:

### Decision 1: Communications are NOT tools
The agent framework handles messaging natively. `send_whatsapp`, `send_sms_fallback` are infrastructure concerns — notifications become side-effects of `manage_booking`, not agent actions.

### Decision 2: Calendar collapsed from 5 to 2
- `check_agent_calendar` + `check_property_availability` → merged into `get_available_slots` (one call, pre-filtered by all availability constraints)
- `create_booking` + `cancel_booking` + `reschedule_booking` → merged into `manage_booking` with an `action` parameter (one resource, multiple operations)

### Decision 3: Skip non-essential tools
- `get_directions` → map link is a field on the property object
- `get_market_data` → nice-to-have, not MVP
- `log_interaction` → conversation history IS the log
- `get_lead_history` → loaded into agent context at session start
- `transfer_to_human` → framework-level escalation

## Phase 3: Domain Organization

Organized 5 tools into 3 domains:

| Domain | Tools | Nature |
|---|---|---|
| Property Catalog | `search_properties`, `get_property_details` | Read-only |
| Scheduling | `get_available_slots`, `manage_booking` | Read + Write |
| CRM | `update_lead` | Write-only |

Each domain = one standalone MCP server.

## Phase 4: Schema Design (Property Catalog)

### search_properties decisions:
- **`purpose` (buy/rent):** Made optional, supports both
- **`bedrooms`:** Minimum filter, not exact match. `bedrooms=2` returns 2, 3, 4+ BR
- **`city`:** Made optional (not required) — agent might search across cities
- **`area`:** Free text with substring matching, case-insensitive. "DHA" matches "DHA Phase 6"
- **`owner_notes`:** Included in search results when available — gives agent scheduling context early
- **Prices in PKR:** Agent converts customer language ("85 lac" → 8500000)
- **Sizes in marla:** 1 kanal = 20 marla, normalized internally

### get_property_details decisions:
- Single input: `property_id`
- Returns everything: description, features, amenities, photos with captions, map_url, owner_notes, viewing_instructions
- `features` vs `amenities` split — selling points vs utilities/infrastructure

## Phase 5: Tech Stack Decisions

### Language: Python with FastMCP
- Ecosystem fit — tutorsgpt stack is all Python
- FastMCP decorator-based tools are simpler than TypeScript's registerTool
- No build step needed
- Pydantic validation already familiar

### Transport: Streamable HTTP
- Remote-capable, multi-client
- Production-ready from day one
- `stateless_http=True, json_response=True` for scalability

### Rejected: TypeScript
Would be better for public MCP server distribution, but for internal agent tooling in a Python shop — Python wins.

## Phase 6: Implementation Pivots

### Pivot 1: lifespan_context, not lifespan_state
The MCP builder reference docs and SDK examples referenced `ctx.request_context.lifespan_state`. The actual SDK uses `ctx.request_context.lifespan_context`. Caught during end-to-end testing — this is exactly why we test the running server, not just unit tests.

### Pivot 2: model_validator instead of field_validator for cross-field checks
Initially planned `@field_validator('budget_max')` for budget range validation, but `budget_min` might not be in `info.data` yet depending on field order. Switched to `@model_validator(mode="after")` which runs after all fields are set — cleaner for cross-field validation.

### Pivot 3: Individual params in tool signature, Pydantic model inside body
FastMCP auto-generates JSON schema from function parameters. Using `params: SearchPropertiesInput` as the function param would work but loses control over error formatting. Instead: individual typed params in the signature (for schema generation), construct the Pydantic model inside the body (for cross-field validation), catch `ValidationError` to return custom error format.

### Pivot 4: Accept header required for streamable HTTP
`curl` calls to the MCP server fail without `Accept: application/json` header. The server returns a `Not Acceptable` error. Easy fix but worth noting for anyone testing manually.

## Phase 7: What Was Built

```
src/property_catalog_mcp/
├── server.py          — FastMCP init, lifespan, tool registration
├── models.py          — Pydantic models, enums, validation
├── data.py            — JSON loader (pure function)
├── __main__.py        — python -m entry point
├── tools/
│   ├── search_properties.py    — filter_properties() + build_search_response()
│   └── get_property_details.py — lookup_property()
└── mock_data/
    └── properties.json — 12 listings across Lahore & Karachi
```

**Test coverage:** 57 unit tests + 5 end-to-end verifications

**Server:** `uv run python -m property_catalog_mcp` → `http://localhost:8000/mcp`

## Key Patterns Established

1. **Tool registration pattern:** Each tool file exports `register_xxx(mcp)` — avoids circular imports while keeping one tool per file
2. **Core logic is pure functions:** `filter_properties()`, `lookup_property()` — directly testable without MCP context
3. **TDD flow:** Write test → watch it fail → implement → watch it pass → end-to-end verify
4. **Error format:** `{"success": false, "error": "...", "code": "ERROR_CODE"}` — consistent across all tools
5. **Mock data:** JSON file loaded via lifespan, swappable for real API later without changing tool logic

## Next Steps

- Build Domain 2: Scheduling MCP server (`get_available_slots`, `manage_booking`)
- Build Domain 3: CRM MCP server (`update_lead`)
- Connect to real property database/API
- Wire all 3 MCP servers to an agent framework
