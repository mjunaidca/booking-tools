# Real Estate Booking Agent — Chat Simulation

## Scenario: Customer wants to view properties in DHA Phase 6, Lahore

```
CUSTOMER: Hi, I'm looking to view a 2-bedroom apartment in DHA Phase 6, Lahore.
           Budget is around 80-90 lac.

AGENT:    Welcome! I'm your property viewing assistant. Let me find matching
          properties for you.
          
          [TOOL: search_properties(location="DHA Phase 6, Lahore", 
           bedrooms=2, budget_min=8000000, budget_max=9000000)]

AGENT:    I found 4 properties matching your criteria:
          1. Street 12 — 2BR, 5 marla, 85 lac (available for viewing)
          2. Street 41 — 2BR, 5 marla, 82 lac (available for viewing)
          3. Commercial Ave — 2BR apartment, 78 lac (already under offer)
          4. Street 9 — 2BR, 7 marla, 88 lac (available for viewing)
          
          Would you like to schedule viewings for any of these?

CUSTOMER: Street 12 and Street 9 look good. Can I see them this Saturday?

AGENT:    Let me check availability for Saturday.
          
          [TOOL: check_agent_calendar(date="2026-04-11")]
          [TOOL: check_property_availability(id="prop_12", date="2026-04-11")]
          [TOOL: check_property_availability(id="prop_9", date="2026-04-11")]

AGENT:    Street 12 is available Saturday between 10am-2pm.
          Street 9 owner is only available Saturday after 3pm.
          
          I can book:
          - 10:30 AM → Street 12
          - 3:30 PM → Street 9
          
          Does that work?

CUSTOMER: 10:30 works. But 3:30 is late — anything on Sunday for Street 9?

AGENT:    [TOOL: check_property_availability(id="prop_9", date="2026-04-12")]

AGENT:    Sunday 11am-1pm is open for Street 9. Want me to book both?
          - Saturday 10:30 AM → Street 12
          - Sunday 11:00 AM → Street 9

CUSTOMER: Perfect, book both.

AGENT:    [TOOL: create_booking(property="prop_12", date="2026-04-11", 
           time="10:30", customer_name=?, customer_phone=?)]

AGENT:    I'll need a few details to confirm:
          - Your full name
          - Phone number
          - Would you like directions sent via WhatsApp?

CUSTOMER: Muhammad Jawad, 0300-1234567. Yes, WhatsApp directions please.

AGENT:    [TOOL: create_booking(property="prop_12", date="2026-04-11", 
           time="10:30", name="Muhammad Jawad", phone="03001234567")]
          [TOOL: create_booking(property="prop_9", date="2026-04-12", 
           time="11:00", name="Muhammad Jawad", phone="03001234567")]
          [TOOL: send_whatsapp(phone="03001234567", template="booking_confirm",
           bookings=[...])]

AGENT:    Both viewings are confirmed! You'll receive:
          - WhatsApp confirmation with addresses + map links
          - Reminder 2 hours before each viewing
          
          Anything else you'd like to know about these properties?

CUSTOMER: What's the monthly rent estimate if I buy Street 12 as investment?

AGENT:    [TOOL: get_market_data(location="DHA Phase 6", type="rental", 
           bedrooms=2)]

AGENT:    2BR rentals in DHA Phase 6 currently range 35,000-50,000/month
          depending on furnishing and floor. Street 12 is ground floor, 
          semi-furnished — likely 40,000-45,000 range.

CUSTOMER: Good. That's all for now, thanks.

AGENT:    [TOOL: update_lead(phone="03001234567", status="viewing_scheduled",
           interest_level="high", notes="Investment buyer, price-sensitive on 
           timing, prefers morning viewings")]

AGENT:    You're all set, Jawad! See you Saturday at 10:30. 
          Call or message anytime if plans change.
```

## Key Observations

- Customer went from inquiry to 2 confirmed bookings in ~8 messages
- Agent needed to coordinate availability across multiple properties and dates
- Investment question required market data — a "nice to have" that builds trust
- Lead tracking happened silently at the end — customer never sees it
