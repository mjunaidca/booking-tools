# Real Estate Booking Agent — Tools Proposal

## Status: Revised (v2)

---

## Tool Inventory: 5 Tools across 3 Domains

### Domain 1: Property Catalog

> **System:** Listings database (own DB or external API like Zameen/Graana)
> **Purpose:** Everything about what's available to view

| Tool | Signature | Purpose |
|---|---|---|
| `search_properties` | `(location, bedrooms?, budget_min?, budget_max?, type?)` | Find matching listings by filters. Returns summary list with IDs, price, key specs, availability status. |
| `get_property_details` | `(property_id)` | Full listing for one property — photos, specs, address, map link, owner notes, viewing instructions. Called when customer says "tell me more." |

**Why 2 tools, not 1?** Search returns lightweight summaries for browsing. Details returns everything for a single property. Keeps search responses fast and readable.

---

### Domain 2: Scheduling

> **System:** Booking/calendar service (own backend)
> **Purpose:** Find slots and lock them

| Tool | Signature | Purpose |
|---|---|---|
| `get_available_slots` | `(property_id, date_range)` | Returns viewable time slots, pre-filtered by both agent and property/owner availability. One call answers "when can we see this?" |
| `manage_booking` | `(action, params)` | `action: "create"` — books a slot (property, date, time, customer name, phone). `action: "cancel"` — cancels by booking ID. `action: "reschedule"` — moves to new slot. Returns confirmation or conflict error. |

**Why 2 tools, not 1?** Checking availability is a read with no side effects. Managing bookings is a write that locks resources. Separating reads from writes prevents accidental bookings and keeps the agent's reasoning clean.

---

### Domain 3: CRM

> **System:** Customer relationship tracking (own backend or CRM like HubSpot)
> **Purpose:** Remember the customer across conversations

| Tool | Signature | Purpose |
|---|---|---|
| `update_lead` | `(customer_phone, status?, interest_level?, preferences?, notes?)` | Records what the agent learned — viewing preferences, budget signals, investment intent, follow-up notes. Upserts by phone number. |

**Why 1 tool?** Reading lead history can be loaded into agent context at conversation start (system prompt injection), so no read tool needed. The agent only needs to *write* what it learned.

---

## What Was Cut and Why

| Original Tool | Reason Removed |
|---|---|
| `send_whatsapp` | Agent framework handles messaging. Notifications are a side-effect of `manage_booking`, not an agent action. |
| `send_sms_fallback` | Same — infrastructure, not agent concern. |
| `check_agent_calendar` | Merged into `get_available_slots` — agent availability is a filter, not a separate lookup. |
| `check_property_availability` | Merged into `get_available_slots` — same reasoning. |
| `cancel_booking` | Merged into `manage_booking` as `action: "cancel"`. |
| `reschedule_booking` | Merged into `manage_booking` as `action: "reschedule"`. |
| `get_directions` | Map link is a field on the property object returned by `get_property_details`. Not an action. |
| `get_market_data` | Nice-to-have, not MVP. Agent can defer: "I can connect you with our analyst for rental estimates." |
| `log_interaction` | Conversation history *is* the log. Framework responsibility. |
| `get_lead_history` | Loaded into context at session start. No tool call needed. |
| `transfer_to_human` | Framework-level escalation, not an agent tool. |

---

## Domain Boundaries

```
┌─────────────────────────────────────────────────┐
│                  AI AGENT                        │
│         (conversation + reasoning)               │
├──────────┬──────────────────┬───────────────────┤
│          │                  │                    │
│  DOMAIN 1│      DOMAIN 2    │     DOMAIN 3       │
│  Property│     Scheduling   │       CRM          │
│  Catalog │                  │                    │
│          │                  │                    │
│ search   │ get_available    │  update_lead       │
│ details  │ manage_booking   │                    │
│          │                  │                    │
│ [READ]   │ [READ + WRITE]   │  [WRITE]           │
│          │                  │                    │
│  Source:  │  Source:         │  Source:            │
│  DB/API  │  Own service     │  CRM system        │
└──────────┴──────────────────┴───────────────────┘
```

---

## Success Metrics

| Level | Metric | Target |
|---|---|---|
| **Conversion** | Inquiry to Booking rate | > 60% |
| | Booking to Show-up rate | > 80% |
| **Speed** | First property suggestion | < 30 seconds |
| | Full booking confirmed | < 3 minutes |
| **Satisfaction** | Completes without human handoff | > 70% |
| **Operational** | Double-bookings | 0 |

---

## Open Design Questions

1. Property data source — own DB vs external API (Zameen, Graana)?
2. Calendar system — Google Calendar vs custom availability slots per property?
3. Multi-party coordination — how much owner interaction does the agent handle?
4. Scope boundary — booking only, or post-viewing follow-up too?
