"""Run a handful of known-good scenarios for demo rehearsal.

Don't rely on live, unpredictable inputs during judging — these three
districts are confirmed to produce clean, varied recommendation output.
Run with: python scripts/demo_scenarios.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from backend.services.message_formatter import format_recommendation
from backend.services.recommendation_service import build_recommendation

SCENARIOS = [
    {"location": "Nashik, Maharashtra", "land_size": 5, "last_crop": "onion"},
    {"location": "Ludhiana, Punjab", "land_size": 8, "last_crop": "wheat"},
    {"location": "Midnapore, West Bengal", "land_size": 3, "last_crop": "skip"},
]


def main():
    for scenario in SCENARIOS:
        print("=" * 70)
        print(f"Scenario: {scenario['location']}, {scenario['land_size']} acres, last grew {scenario['last_crop']}")
        print("-" * 70)
        recommendation = build_recommendation(
            scenario["location"], scenario["land_size"], scenario["last_crop"]
        )
        print(format_recommendation(recommendation))
        print()


if __name__ == "__main__":
    main()
