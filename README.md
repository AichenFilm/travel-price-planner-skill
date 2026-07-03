# Travel Price Planner Skill

An English, general-purpose Codex skill for comparing flights, hotels, trains, and mixed travel itineraries by total cost and practical risk.

The goal is not to promise the absolute lowest price on the internet. The goal is to find the lowest reasonable option after considering final payable price, baggage, taxes, fees, refund/change rules, cancellation policy, booking party, aftersales, self-transfer risk, transit/visa uncertainty, and local transport costs.

## What It Does

- Compares official sites, metasearch tools, OTAs, hotel sites, and rail operators.
- Separates list price from final payable total.
- Flags risky cheap options such as separate tickets, self-transfer, unclear baggage, login-only prices, nonrefundable hotels, and unclear ticketing parties.
- Gives a clear booking path instead of only listing prices.
- Includes a deterministic quote normalizer for manually collected CSV rows.

## Installation

Copy the `travel-price-planner` folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R travel-price-planner ~/.codex/skills/
```

Then invoke it with prompts such as:

```text
Use $travel-price-planner to compare flights from Paris to Tokyo in October.
Use $travel-price-planner to compare hotels near a conference venue with free cancellation.
Use $travel-price-planner to decide whether Trainline is worth using over the official rail operator.
```

## CSV Normalizer

The bundled script does not scrape or fetch prices. It only normalizes quotes you already collected.

```bash
python3 travel-price-planner/scripts/normalize_travel_quotes.py quotes.csv --base-currency EUR --fx USD=0.92 --format markdown
```

Minimum useful columns:

```csv
label,category,source,currency,total_price,mandatory_fees,baggage_fee,payment_fee,local_transport_cost,risk_flags,booking_party,url,notes
```

## Safety Boundaries

This skill does not book, pay, log in, enter personal data, store credentials, bypass captchas, or use stealth/anti-detection scraping. Travel prices and entry rules change quickly; verify final price and legal/entry requirements with the provider or official source before purchase.

## Tests

```bash
python3 -m unittest discover -s tests
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py travel-price-planner
```

## License

MIT
