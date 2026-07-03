---
name: travel-price-planner
description: Travel planning and price comparison for flights, hotels, trains, and mixed itineraries. Use when Codex needs to compare Google Flights, airline or rail official sites, Trip.com, Skyscanner, Kayak, Booking.com, Agoda, Expedia, Trainline, Omio, 12306, hotel official sites, or similar travel sources; find the lowest reasonable total cost; evaluate baggage, taxes, fees, refund/change rules, OTA aftersales, self-transfer, visa/transit, hotel cancellation, rail fare, or hidden-cost risks; or explain whether a metasearch tool can replace an OTA or official booking channel.
---

# Travel Price Planner

## Core Rule

Find the lowest reasonable option, not the lowest naked list price. Compare final payable cost, required add-ons, schedule fit, ticketing party, aftersales, refund/change/cancellation terms, and connection or stay risk before recommending a booking path.

Do not book, pay, log in, enter personal data, store credentials, bypass captchas, or use stealth or anti-detection scraping. Stop before purchase or account actions and ask for explicit user confirmation.

## Workflow

1. Collect only missing high-impact constraints: date flexibility, origin/destination flexibility, travelers, bags, must-arrive time, budget ceiling, refund needs, payment currency, visa/transit limits, lodging area, cancellation needs, and rail time preferences.
2. Read `references/default-preferences.md` when the user has not stated their preferences or when you need a reusable preference template.
3. Read `references/source-matrix.md` to choose search sources by travel type and region.
4. Check live prices through normal web or browser access, using official sources first when final verification matters. Record source URL, timestamp and timezone, currency, final displayed total, ticketing/booking party, baggage or breakfast, cancellation/refund/change terms, and visible fees.
5. Read `references/risk-rules.md` whenever an option involves OTA booking, self-transfer, separate tickets, unclear baggage, nonrefundable lodging, rail agents, transit countries, unusual discounts, login-only prices, or a volatile event period.
6. Read `references/scoring-model.md` to rank options by total cost and booking risk.
7. If there are many quote rows, assemble a CSV and run `scripts/normalize_travel_quotes.py` to produce a deterministic comparison table. The script normalizes manually collected quotes only; it does not fetch live prices.
8. Present a recommendation with: best overall option, cheapest acceptable option, options to avoid, exact booking route, and what to verify on the final checkout page.

## Source Strategy

- Flights: start with a metasearch source such as Google Flights for date and route discovery, then verify the strongest itinerary on the airline official site. Use OTAs and secondary metasearch sources only to check whether a meaningful price gap exists.
- Hotels: start with a map or hotel metasearch source for area and price range, then compare major OTAs and the property official site. Compare final taxes, fees, room type, cancellation, deposit, breakfast, and location-adjusted transport cost.
- Trains: prioritize official rail operators for fare class and rules. Use Trainline, Omio, Trip.com, or similar agents for comparison, convenience, or multimodal discovery.
- APIs such as Skyscanner, Amadeus, Duffel, Hotelbeds, or Expedia Rapid require legitimate accounts and user-provided environment variables. Do not invent API access or imply live API coverage when it is not configured.

## Output Standard

Distinguish these tiers:

- `recommended`: best total cost/risk balance.
- `cheapest acceptable`: cheapest option that is still practically bookable.
- `optional`: acceptable, but neither the strongest overall nor the cheapest acceptable option.
- `cheaper but risky`: lower price with material aftersales, refund, baggage, transfer, visa, or hidden-fee risk.
- `avoid`: do not recommend unless the user explicitly accepts the risk.

For each recommended option, include a concrete booking path, such as `Google Flights -> airline official site`, `Booking.com refundable rate`, `Trenitalia official site`, or `12306 official site`.

Keep original-language fare rules, cancellation text, baggage rules, and platform names when precision matters, then explain them plainly in the user's language.

## Script Use

Use the normalizer after collecting quote rows:

```bash
python3 /path/to/travel-price-planner/scripts/normalize_travel_quotes.py quotes.csv --base-currency EUR --fx USD=0.92 --fx CNY=0.127 --direct-margin 50 --format markdown
```

Resolve the script path relative to this skill directory. Do not assume the current working directory is the skill directory.

Minimum useful CSV columns:

```csv
label,category,source,currency,total_price,mandatory_fees,baggage_fee,payment_fee,local_transport_cost,risk_flags,booking_party,url,notes
```

Risk flags are semicolon-separated, for example `ota;no_checked_bag;self_transfer;nonrefundable`.

## Final Safety Check

Before recommending "book now", verify the option on the checkout or official detail page if reachable, then state the timestamp. If final checkout cannot be reached without login or personal data entry, say so and treat the price as provisional.
