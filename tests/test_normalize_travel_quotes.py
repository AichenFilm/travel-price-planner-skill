#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "travel-price-planner" / "scripts" / "normalize_travel_quotes.py"

spec = importlib.util.spec_from_file_location("normalize_travel_quotes", SCRIPT)
normalizer = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = normalizer
spec.loader.exec_module(normalizer)


class NormalizeTravelQuotesTest(unittest.TestCase):
    def test_direct_booking_beats_small_ota_saving(self) -> None:
        rows = [
            {
                "label": "Airline official",
                "category": "flight",
                "source": "Airline",
                "currency": "EUR",
                "total_price": "590",
                "risk_flags": "basic_or_promo_fare",
                "booking_party": "Airline",
            },
            {
                "label": "OTA small saving",
                "category": "flight",
                "source": "Trip.com",
                "currency": "EUR",
                "total_price": "560",
                "risk_flags": "ota;basic_or_promo_fare",
                "booking_party": "Trip.com",
            },
        ]
        quotes = [normalizer.normalize_row(row, "EUR", {}) for row in rows]
        ranked = normalizer.rank_quotes(quotes, direct_margin=50)
        tiers = {quote.label: quote.tier for quote in ranked}
        self.assertEqual(tiers["Airline official"], "recommended")
        self.assertEqual(tiers["OTA small saving"], "cheapest acceptable")

    def test_large_ota_saving_can_win_when_risk_is_bounded(self) -> None:
        rows = [
            {
                "label": "Official",
                "category": "flight",
                "source": "Airline",
                "currency": "EUR",
                "total_price": "900",
                "risk_flags": "",
                "booking_party": "Airline",
            },
            {
                "label": "Major OTA",
                "category": "flight",
                "source": "Expedia",
                "currency": "EUR",
                "total_price": "720",
                "risk_flags": "ota",
                "booking_party": "Expedia",
            },
        ]
        quotes = [normalizer.normalize_row(row, "EUR", {}) for row in rows]
        ranked = normalizer.rank_quotes(quotes, direct_margin=50)
        tiers = {quote.label: quote.tier for quote in ranked}
        self.assertEqual(tiers["Major OTA"], "recommended")
        self.assertEqual(tiers["Official"], "optional")

    def test_hard_avoid_and_high_risk_tiers(self) -> None:
        rows = [
            {
                "label": "Unknown reseller",
                "category": "flight",
                "source": "Unknown",
                "currency": "EUR",
                "total_price": "400",
                "risk_flags": "unknown_booking_party",
            },
            {
                "label": "Separate tickets",
                "category": "flight",
                "source": "Metasearch",
                "currency": "EUR",
                "total_price": "450",
                "risk_flags": "separate_tickets;ota",
            },
        ]
        quotes = [normalizer.normalize_row(row, "EUR", {}) for row in rows]
        ranked = normalizer.rank_quotes(quotes)
        tiers = {quote.label: quote.tier for quote in ranked}
        self.assertEqual(tiers["Unknown reseller"], "avoid")
        self.assertEqual(tiers["Separate tickets"], "cheaper but risky")

    def test_money_formats_and_fx(self) -> None:
        row = {
            "label": "Dollar quote",
            "category": "hotel",
            "source": "Hotel",
            "currency": "USD",
            "total_price": "US$1,200.50",
            "mandatory_fees": "20",
            "risk_flags": "",
        }
        quote = normalizer.normalize_row(row, "EUR", {"USD": 0.9})
        self.assertEqual(quote.total_cost_original, 1220.5)
        self.assertEqual(quote.total_cost_base, 1098.45)

    def test_unknown_flag_fails(self) -> None:
        row = {
            "label": "Bad flag",
            "category": "train",
            "source": "Agent",
            "currency": "EUR",
            "total_price": "30",
            "risk_flags": "made_up_flag",
        }
        with self.assertRaises(ValueError):
            normalizer.normalize_row(row, "EUR", {})

    def test_markdown_escapes_pipes(self) -> None:
        quote = normalizer.normalize_row(
            {
                "label": "Hotel | center",
                "category": "hotel",
                "source": "Official | site",
                "currency": "EUR",
                "total_price": "100",
                "risk_flags": "",
                "notes": "Queen | refundable",
            },
            "EUR",
            {},
        )
        normalizer.rank_quotes([quote])
        output = normalizer.format_markdown([quote])
        self.assertIn("Hotel / center", output)
        self.assertIn("Official / site", output)
        self.assertIn("Queen / refundable", output)

    def test_cli_markdown_and_missing_fx(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "quotes.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "label",
                        "category",
                        "source",
                        "currency",
                        "total_price",
                        "risk_flags",
                        "booking_party",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "label": "Official rail",
                        "category": "train",
                        "source": "Official",
                        "currency": "EUR",
                        "total_price": "49",
                        "risk_flags": "",
                        "booking_party": "Official rail",
                    }
                )
            ok = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--base-currency", "EUR", "--format", "markdown"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertIn("recommended", ok.stdout)

            missing_fx = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--base-currency", "USD"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(missing_fx.returncode, 2)
            self.assertIn("Missing FX rate for EUR", missing_fx.stderr)


if __name__ == "__main__":
    unittest.main()
