# Real Estate Booking Tools

## What We're Building

AI-powered tools that let a real estate booking agent handle property viewing appointments end-to-end. The agent converses with customers, finds matching properties, checks availability, and books viewings — no human in the loop for standard flows.

This is **not** the agent itself. This repo contains the **tools** (functions/APIs) the agent calls. The agent framework (conversation, messaging, memory) is handled separately.

## Goal

Build a minimal, working set of tools that let an AI agent take a customer from "I want to see a 2BR in DHA Phase 6" to a confirmed viewing appointment in under 3 minutes.

## Current Focus

Building **MCP (Model Context Protocol) servers** — one per domain. Each domain becomes a standalone MCP server that any agent framework can connect to.

## Architecture

```
Customer ←→ AI Agent (framework) ←→ MCP Servers (this repo) ←→ Backend Systems
                                      ├── property-catalog-mcp
                                      ├── scheduling-mcp
                                      └── crm-mcp
```

The agent framework handles conversation and messaging. This repo provides MCP servers exposing the 5 tools the agent calls to do real work.

## Tool Inventory (5 tools, 3 domains)

### Domain 1: Property Catalog (read-only)
- `search_properties(location, bedrooms?, budget_min?, budget_max?, type?)` — find matching listings
- `get_property_details(property_id)` — full listing info, photos, map link

### Domain 2: Scheduling (read + write)
- `get_available_slots(property_id, date_range)` — available viewing times, pre-filtered by agent + owner availability
- `manage_booking(action, params)` — create, cancel, or reschedule a viewing

### Domain 3: CRM (write-only)
- `update_lead(customer_phone, status?, interest_level?, preferences?, notes?)` — record customer insights

## Design Decisions

- **Communications are NOT tools.** The agent framework handles messaging. Notifications (WhatsApp confirmations, reminders) are side-effects of booking creation, not agent actions.
- **Calendar is unified.** Agent availability + property/owner availability = one `get_available_slots` call. No separate calendar lookups.
- **Booking lifecycle is one tool.** Create/cancel/reschedule are actions on the same resource, handled by `manage_booking` with an `action` parameter.
- **Lead history is context, not a tool.** Customer data is loaded into the agent's system prompt at conversation start. Only writes go through a tool.
- **Market data, directions, escalation are deferred.** Not MVP. Add when the core booking loop works.

## Success Criteria

| Metric | Target |
|---|---|
| Inquiry to Booking rate | > 60% |
| Booking to Show-up rate | > 80% |
| First property suggestion | < 30 seconds |
| Full booking confirmed | < 3 minutes |
| Double-bookings | 0 |

## Project Structure

```
booking-tools/
├── CLAUDE.md              ← you are here
├── research/
│   ├── simulation.md      ← chat simulation showing tool usage in context
│   └── tools_proposal.md  ← tool design rationale, what was cut and why
└── src/                   ← tool implementations (coming)
```

## Approach

1. **Simulation first** (done) — understand the conversation flow and what tools get called
2. **Tool design** (done) — cut 15 tools to 5, organized by domain
3. **Schema design** (next) — define exact input/output contracts for each tool
4. **Stub implementation** — tools return mock data, agent can run end-to-end
5. **Real backends** — connect to actual property DB, calendar system, CRM

## Development Rules

### TDD is mandatory
- Write tests FIRST, then implement to make them pass
- No implementation code without a failing test driving it

### End-to-end verification before reporting
- Don't just run unit tests and call it done
- Start the MCP server, test tools end-to-end, verify the full flow works
- Only inform the user something is ready after you've confirmed it works yourself

## Conventions

- Each domain = one MCP server
- Tool functions are the unit of work — each tool = one file
- Tools are stateless — all state lives in the backend systems they call
- Error responses use a consistent format: `{success: false, error: string, code: string}`
- All tools validate inputs before calling backends
