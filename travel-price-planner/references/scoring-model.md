# Scoring Model

Use this model as a disciplined comparison aid. It is not a substitute for judgment.

## Required Fields

For each quote, try to collect:

- Label: short human-readable option name.
- Category: flight, hotel, train, package, or mixed.
- Source and URL.
- Query timestamp and timezone.
- Currency and final displayed total.
- Mandatory fees, baggage fee, payment fee, local transport cost, or other required add-ons.
- Booking party or ticketing party.
- Refund/change/cancellation terms.
- Included baggage, breakfast, or seat details where relevant.
- Risk flags and notes.

## Total Cost

Calculate:

`total_cost = displayed_total + mandatory_fees + baggage_fee + payment_fee + local_transport_cost + other_required_costs`

Do not include optional comfort upgrades unless the user asked for them. Do include costs needed to make options comparable, such as checked baggage when one option includes it and another does not.

## Risk Score

Start at 0 and add points:

| Flag | Points |
|---|---:|
| `ota` | 1 |
| `unknown_booking_party` | 4 |
| `price_not_final` | 3 |
| `login_or_coupon_only` | 2 |
| `no_checked_bag` | 2 |
| `unclear_baggage` | 3 |
| `basic_or_promo_fare` | 2 |
| `nonrefundable` | 3 |
| `change_fee_high` | 2 |
| `self_transfer` | 5 |
| `separate_tickets` | 5 |
| `short_connection` | 4 |
| `overnight_transfer` | 3 |
| `visa_or_transit_unclear` | 5 |
| `taxes_excluded` | 2 |
| `city_tax_excluded` | 1 |
| `room_type_unclear` | 3 |
| `poor_location` | 3 |
| `agent_service_fee` | 1 |
| `rail_validation_unclear` | 2 |
| `strike_or_disruption_risk` | 3 |
| `custom_high_risk` | 4 |

If a serious risk is present but no flag fits, add `custom_high_risk` and explain the 3-5 point risk in notes.

## Tier Rules

- `recommended`: low or moderate risk, good total cost, clear booking path, and no unresolved high-impact uncertainty.
- `cheapest acceptable`: cheapest option that remains bookable with risks understood and manageable.
- `optional`: acceptable, but neither the best overall nor the cheapest acceptable option.
- `cheaper but risky`: cheaper than safer options but has material risk that the user must explicitly accept.
- `avoid`: unclear final price, unclear booking party, unprotected transfer, serious visa/transit uncertainty, or small savings with large aftersales risk.

Suggested numeric mapping:

- 0-2 points: low risk.
- 3-5 points: moderate risk.
- 6-9 points: high risk.
- 10+ points: very high risk.

## Recommendation Logic

1. Remove or demote options with unreproducible final price or unclear booking party.
2. Identify the lowest total cost among acceptable options.
3. Identify the best official/direct option.
4. Compare savings against added risk.
5. Recommend direct/official booking when the savings from an OTA are small.
6. Recommend an OTA only when savings are meaningful and the risk is explicit, bounded, and acceptable.

The normalizer uses `--direct-margin` to prefer direct/official booking when it is within that amount of the cheapest acceptable option. Default margin is 50 in the chosen base currency.

Always explain the tradeoff in plain language.
