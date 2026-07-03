# Risk Rules

Use these rules to identify when a cheap option is not actually the best option.

## Universal Risks

- Treat prices as volatile. Record query timestamp, timezone, and whether the price was confirmed on the final checkout page.
- Compare final payable total, not list price. Add required baggage, taxes, payment fees, city taxes, service fees, seat fees, and unavoidable local transport.
- Mark login-only, coupon-only, app-only, or member-only prices as conditional.
- Do not recommend a booking path if the ticketing or booking party is unclear.
- Do not enter passenger names, payment details, account credentials, passport numbers, identity numbers, or loyalty numbers without explicit confirmation.

## OTA and Aftersales Risk

Flag an OTA option when:

- The OTA is much cheaper than both official site and major competitors.
- Refund/change terms are summarized vaguely rather than shown as fare rules.
- The platform sells separate tickets as if they were one itinerary.
- Baggage differs from the airline or operator official display.
- Customer service would be needed across language or timezone barriers.
- The price is not reproducible on the final payment page.

Default judgment:

- OTA within 30-50 units of the base currency of the official site for medium/long-haul travel: usually prefer official.
- OTA more than 80-100 units cheaper: consider only after baggage, refund, ticketing, and connection protection are verified.

## Flight Risks

Flag as high risk:

- Self-transfer, separate PNRs, or separate tickets.
- Short connection without airline protection.
- Overnight airport transfer requiring extra hotel or transport.
- Checked baggage not included when the user likely needs it.
- Basic economy or promotional fare with no refund and expensive changes.
- Transit through a country where visa, entry, or airport-transfer rules may matter.
- Arrival time that creates missed train, hotel check-in, or onward transport risk.

Special handling:

- Codeshare or interline itineraries are acceptable only when sold as one protected itinerary by an airline or reputable OTA with clear ticketing.
- If passport, residence permit, visa, nationality, or transit status matters, ask or verify with official sources before recommending.

## Hotel Risks

Flag as high risk:

- Nonrefundable rate during event periods or uncertain travel dates.
- Room type ambiguity: single/double/twin, shared bathroom, external bathroom, sofa bed, or "selected at check-in".
- Taxes, city tax, resort fee, or service fee excluded.
- Deposit, prepayment, cash-only, or late-arrival constraints.
- Poor location that creates large transport cost or unsafe late-night arrival.
- Review pattern showing cleanliness, check-in, noise, or cancellation disputes.

Default judgment:

- During high-demand periods, a slightly higher free-cancellation rate can be better than the cheapest nonrefundable rate.
- Compare location-adjusted cost: hotel price plus local transport, time, and late-night arrival risk.

## Train Risks

Flag as high risk:

- Agent fee makes Trainline, Omio, Trip.com, or another agent meaningfully more expensive than official.
- Fare class is non-changeable or nonrefundable and the user's schedule is uncertain.
- Regional tickets may require validation, check-in, or activation rules.
- Tight train connection after a flight arrival.
- Strike risk, major works, or disruption is reported for the date/route.

Default judgment:

- For simple routes, prefer official rail sites when price is close.
- Use agents when multi-operator discovery, language support, payment support, or convenience outweighs small fees.

## Avoid Recommendation

Put an option in `avoid` when at least one applies:

- The final price cannot be reproduced.
- The booking party is unclear.
- The itinerary relies on risky self-transfer without enough buffer.
- Serious visa, entry, or transit uncertainty remains.
- The savings are small but aftersales/refund risk is large.
- The option requires credentials, coupons, app-only prices, or payment methods the user has not confirmed.
