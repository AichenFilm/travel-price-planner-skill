# Source Matrix

Use this matrix to choose search sources and trust levels. Prefer official sources for final verification, especially when refund, changes, baggage, visa, or support risk matters.

## Flights

| Source | Use For | Strength | Watchouts |
|---|---|---|---|
| Google Flights or similar flight metasearch | First-pass route/date discovery, calendar view, airline/OTA links | Fast comparison and date flexibility | Not the booking or aftersales party; some carriers/fares may be missing; prices can lag |
| Airline official site | Final verification and preferred booking | Clear ticketing party; better for changes, refunds, baggage, and disruption handling | Sometimes slightly higher; multi-airline itineraries may be harder |
| Trip.com / Ctrip | China-facing comparison, Chinese support, China domestic travel | Familiar China inventory and support | Confirm ticketing party, baggage, refund/change rules, currency, and fees |
| Skyscanner | Airline/OTA price discovery | Broad market scan and deep links | Results may lead to weak OTAs; final price can change |
| Kayak / Momondo | Secondary metasearch check | Useful for catching outliers | Same OTA and price freshness risks |
| Expedia or regional OTA | Flight plus hotel packages or regional comparison | Packages can be useful | Aftersales, fare rules, and service fees must be verified |

Flight search order:

1. Use metasearch for dates, airports, airlines, and rough low-price patterns.
2. Verify the best candidate on the airline official site.
3. Check one major OTA and one secondary metasearch source when the price gap may matter.
4. If an OTA is much cheaper, verify final checkout price, ticketing party, baggage, refund/change rules, and customer-service risk before recommending.

## Hotels

| Source | Use For | Strength | Watchouts |
|---|---|---|---|
| Google Hotels / Maps or similar maps | Area and price range discovery | Map context and cross-platform overview | Click through to verify final taxes and conditions |
| Booking.com | Europe and global baseline | Strong inventory and cancellation visibility | City tax, payment timing, room type, login prices |
| Agoda | Asia and discount comparison | Often competitive prices | Tax/fee display, cancellation details, support risk |
| Trip.com / Ctrip | China-facing hotel comparison | Useful China inventory and Chinese support | Verify room naming, cancellation, tax/fees |
| Expedia / Hotels.com | OTA comparison and packages | Useful member rates and packages | Loyalty rates and cancellation terms vary |
| Hotel official site | Final verification and direct booking option | Direct relationship with property, sometimes perks | Price may be higher; cancellation rules still vary |

Hotel search order:

1. Establish neighborhoods and transport cost with map or hotel metasearch.
2. Compare major OTAs and the property official site for shortlisted properties.
3. Compare final payable price, not list price: taxes, city tax, resort fee, breakfast, cancellation, deposit, payment timing, and room type.

## Trains

| Source | Use For | Strength | Watchouts |
|---|---|---|---|
| National or operator official rail site | Official rail inventory and rules | Official fares and fare conditions | Validation rules, fare class, refund/exchange rules |
| Trainline | Europe rail comparison and convenience | Useful multi-operator comparison and digital tickets | Service fee, aftersales through agent, fare-rule clarity |
| Omio | Multimodal Europe comparison | Train/bus/flight comparison | Service fee and aftersales terms |
| 12306 | China rail official | Official ticketing and rules | Account/payment/user access may be needed |
| Trip.com / Ctrip | China rail convenience | Familiar interface and support | Agent service fee and refund/change details |

Train search order:

1. Use official rail sites first for exact fare classes and rules.
2. Use agents as comparison or convenience layers.
3. Prefer official booking when price is close and plans may change.

## Optional API Sources

Use only when the user has legitimate API access and provides keys through environment variables:

- Skyscanner Live Prices API for structured flight offers.
- Amadeus or Duffel for flight search or booking infrastructure.
- Hotelbeds or Expedia Rapid for lodging inventory.

Do not claim API coverage exists unless access has been confirmed in the current environment.
