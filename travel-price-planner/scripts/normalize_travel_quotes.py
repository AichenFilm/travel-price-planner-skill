#!/usr/bin/env python3
"""Normalize manually collected travel quotes into ranked comparison output.

This script does not fetch live prices. It only processes quote rows collected
from web/browser/API checks and applies a deterministic cost/risk model.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


RISK_POINTS = {
    "ota": 1,
    "unknown_booking_party": 4,
    "price_not_final": 3,
    "login_or_coupon_only": 2,
    "no_checked_bag": 2,
    "unclear_baggage": 3,
    "basic_or_promo_fare": 2,
    "nonrefundable": 3,
    "change_fee_high": 2,
    "self_transfer": 5,
    "separate_tickets": 5,
    "short_connection": 4,
    "overnight_transfer": 3,
    "visa_or_transit_unclear": 5,
    "taxes_excluded": 2,
    "city_tax_excluded": 1,
    "room_type_unclear": 3,
    "poor_location": 3,
    "agent_service_fee": 1,
    "rail_validation_unclear": 2,
    "strike_or_disruption_risk": 3,
    "custom_high_risk": 4,
}

HARD_AVOID_FLAGS = {
    "unknown_booking_party",
    "self_transfer",
    "separate_tickets",
    "visa_or_transit_unclear",
}

MONEY_FIELDS = [
    "total_price",
    "mandatory_fees",
    "baggage_fee",
    "payment_fee",
    "local_transport_cost",
    "other_required_costs",
]

OTA_SOURCE_HINTS = {
    "agoda",
    "booking.com",
    "ctrip",
    "expedia",
    "google flights",
    "google hotels",
    "hotels.com",
    "kayak",
    "momondo",
    "omio",
    "qunar",
    "skyscanner",
    "trainline",
    "trip.com",
}

TIER_RECOMMENDED = "recommended"
TIER_CHEAPEST = "cheapest acceptable"
TIER_OPTIONAL = "optional"
TIER_RISKY = "cheaper but risky"
TIER_AVOID = "avoid"


@dataclass
class NormalizedQuote:
    label: str
    category: str
    source: str
    booking_party: str
    currency: str
    total_cost_original: float
    base_currency: str
    total_cost_base: float
    risk_score: int
    risk_level: str
    tier: str
    risk_flags: list[str]
    url: str
    notes: str


def parse_money(value: str | None) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    cleaned = text.strip()
    for token in [
        "US$",
        "CN\u00a5",
        "RMB",
        "EUR",
        "USD",
        "CNY",
        "GBP",
        "JPY",
        "\u20ac",
        "$",
        "\u00a5",
        "\uffe5",
        "\u00a3",
    ]:
        cleaned = cleaned.replace(token, "")
    cleaned = cleaned.strip()
    if "," in cleaned and "." in cleaned and cleaned.rfind(",") > cleaned.rfind("."):
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned and "." not in cleaned:
        comma_tail = cleaned.rsplit(",", 1)[-1]
        cleaned = cleaned.replace(",", ".") if len(comma_tail) == 2 else cleaned.replace(",", "")
    else:
        unsigned = cleaned
        sign = ""
        if unsigned.startswith(("+", "-")):
            sign = unsigned[0]
            unsigned = unsigned[1:]
        dot_parts = unsigned.split(".")
        if (
            "." in unsigned
            and 1 <= len(dot_parts[0]) <= 3
            and len(dot_parts) > 1
            and all(part.isdigit() for part in dot_parts)
            and all(len(part) == 3 for part in dot_parts[1:])
        ):
            cleaned = sign + "".join(dot_parts)
        else:
            cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Cannot parse money value {value!r}") from exc


def parse_fx(values: list[str]) -> dict[str, float]:
    rates: dict[str, float] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"FX rate must look like USD=0.92, got {item!r}")
        currency, rate = item.split("=", 1)
        rates[currency.strip().upper()] = float(rate)
    return rates


def parse_flags(value: str | None) -> list[str]:
    if not value:
        return []
    return [flag.strip() for flag in str(value).replace(",", ";").split(";") if flag.strip()]


def risk_level(score: int) -> str:
    if score <= 2:
        return "low"
    if score <= 5:
        return "moderate"
    if score <= 9:
        return "high"
    return "very_high"


def should_avoid(score: int, flags: set[str]) -> bool:
    if flags & {"unknown_booking_party", "price_not_final", "visa_or_transit_unclear"}:
        return True
    return score >= 10


def is_high_risk(score: int, flags: set[str]) -> bool:
    if flags & HARD_AVOID_FLAGS:
        return True
    return score >= 6


def has_ota_hint(value: str) -> bool:
    text = " ".join(value.lower().split())
    if text in {"booking", "booking.com"}:
        return True
    return any(hint in text for hint in OTA_SOURCE_HINTS)


def is_direct_booking(quote: NormalizedQuote) -> bool:
    if "ota" in quote.risk_flags or "agent_service_fee" in quote.risk_flags:
        return False
    booking_party = quote.booking_party.lower()
    if booking_party:
        return not has_ota_hint(booking_party)
    return not has_ota_hint(quote.source)


def unknown_flags(flags: list[str]) -> list[str]:
    return [flag for flag in flags if flag not in RISK_POINTS]


def normalize_row(row: dict[str, str], base_currency: str, fx: dict[str, float]) -> NormalizedQuote:
    currency = (row.get("currency") or base_currency).strip().upper()
    total_original = sum(parse_money(row.get(field)) for field in MONEY_FIELDS)
    if total_original == 0:
        raise ValueError(f"Row has no parseable price: {row}")
    if currency == base_currency:
        total_base = total_original
    else:
        if currency not in fx:
            raise ValueError(f"Missing FX rate for {currency}; pass --fx {currency}=<rate_to_{base_currency}>")
        total_base = total_original * fx[currency]

    flags = parse_flags(row.get("risk_flags"))
    unknown = unknown_flags(flags)
    if unknown:
        allowed = ", ".join(sorted(RISK_POINTS))
        label = row.get("label") or row.get("option") or "Unnamed option"
        raise ValueError(f"Unknown risk flag(s) for {label!r}: {', '.join(unknown)}. Allowed flags: {allowed}")
    score = sum(RISK_POINTS.get(flag, 0) for flag in flags)
    if row.get("risk_score"):
        score += max(0, int(parse_money(row.get("risk_score"))))

    return NormalizedQuote(
        label=(row.get("label") or row.get("option") or "Unnamed option").strip(),
        category=(row.get("category") or "travel").strip(),
        source=(row.get("source") or "").strip(),
        booking_party=(row.get("booking_party") or "").strip(),
        currency=currency,
        total_cost_original=round(total_original, 2),
        base_currency=base_currency,
        total_cost_base=round(total_base, 2),
        risk_score=score,
        risk_level=risk_level(score),
        tier="",
        risk_flags=flags,
        url=(row.get("url") or "").strip(),
        notes=(row.get("notes") or "").strip(),
    )


def rank_quotes(quotes: list[NormalizedQuote], direct_margin: float = 50.0) -> list[NormalizedQuote]:
    for category in {quote.category for quote in quotes}:
        category_quotes = [quote for quote in quotes if quote.category == category]
        acceptable_quotes = [
            quote
            for quote in category_quotes
            if not should_avoid(quote.risk_score, set(quote.risk_flags))
            and not is_high_risk(quote.risk_score, set(quote.risk_flags))
        ]
        cheapest_acceptable = (
            min(quote.total_cost_base for quote in acceptable_quotes)
            if acceptable_quotes
            else min(quote.total_cost_base for quote in category_quotes)
        )
        direct_candidates = [
            quote
            for quote in acceptable_quotes
            if is_direct_booking(quote) and quote.total_cost_base <= cheapest_acceptable + direct_margin
        ]
        if direct_candidates:
            best_quote = min(direct_candidates, key=lambda q: (q.risk_score, q.total_cost_base))
        elif acceptable_quotes:
            risk_penalty = max(10.0, direct_margin / 2)
            best_quote = min(
                acceptable_quotes,
                key=lambda q: (q.total_cost_base + q.risk_score * risk_penalty, q.risk_score),
            )
        else:
            best_quote = min(category_quotes, key=lambda q: (q.risk_score, q.total_cost_base))

        for quote in category_quotes:
            flags = set(quote.risk_flags)
            if should_avoid(quote.risk_score, flags):
                quote.tier = TIER_AVOID
            elif is_high_risk(quote.risk_score, flags):
                quote.tier = TIER_RISKY
            elif quote is best_quote:
                quote.tier = TIER_RECOMMENDED
            elif math.isclose(quote.total_cost_base, cheapest_acceptable, rel_tol=0.0, abs_tol=0.01):
                quote.tier = TIER_CHEAPEST
            else:
                quote.tier = TIER_OPTIONAL
    return sorted(quotes, key=lambda q: (q.category, tier_sort_key(q.tier), q.risk_score, q.total_cost_base))


def tier_sort_key(tier: str) -> int:
    order = {
        TIER_RECOMMENDED: 0,
        TIER_CHEAPEST: 1,
        TIER_OPTIONAL: 2,
        TIER_RISKY: 3,
        TIER_AVOID: 4,
    }
    return order.get(tier, 9)


def format_markdown(quotes: list[NormalizedQuote]) -> str:
    lines = [
        "| Category | Tier | Option | Source | Total | Risk | Flags | Notes |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for quote in quotes:
        safe_label = markdown_cell(quote.label)
        label = f"[{safe_label}]({quote.url})" if quote.url else safe_label
        flags = markdown_cell("; ".join(quote.risk_flags)) if quote.risk_flags else "-"
        notes = markdown_cell(quote.notes) if quote.notes else "-"
        source = markdown_cell(quote.source or quote.booking_party or "-")
        lines.append(
            f"| {markdown_cell(quote.category)} | {quote.tier} | {label} | {source} | "
            f"{quote.total_cost_base:.2f} {quote.base_currency} | "
            f"{quote.risk_level} ({quote.risk_score}) | {flags} | {notes} |"
        )
    return "\n".join(lines)


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "/").replace("\n", " ").strip()


def write_csv(quotes: list[NormalizedQuote]) -> str:
    fieldnames = list(asdict(quotes[0]).keys()) if quotes else []
    output = sys.stdout
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for quote in quotes:
        data = asdict(quote)
        data["risk_flags"] = ";".join(quote.risk_flags)
        writer.writerow(data)
    return ""


def load_quotes(path: Path, base_currency: str, fx: dict[str, float]) -> list[NormalizedQuote]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Input CSV has no rows")
    return [normalize_row(row, base_currency, fx) for row in rows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="CSV file of manually collected quotes")
    parser.add_argument("--base-currency", default="EUR", help="Comparison currency, default EUR")
    parser.add_argument(
        "--fx",
        action="append",
        default=[],
        help="FX rate into base currency, e.g. USD=0.92. Repeat as needed.",
    )
    parser.add_argument(
        "--direct-margin",
        type=float,
        default=50.0,
        help="Prefer direct/official booking when it is within this amount of the cheapest acceptable option.",
    )
    parser.add_argument("--format", choices=["markdown", "csv", "json"], default="markdown")
    args = parser.parse_args(argv)

    base_currency = args.base_currency.upper()
    try:
        fx = parse_fx(args.fx)
        quotes = rank_quotes(load_quotes(args.csv_path, base_currency, fx), direct_margin=args.direct_margin)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        print(format_markdown(quotes))
    elif args.format == "json":
        print(json.dumps([asdict(quote) for quote in quotes], ensure_ascii=False, indent=2))
    else:
        write_csv(quotes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
