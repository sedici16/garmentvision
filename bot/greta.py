"""Greta Mode: LLM environmental judgment on garment impact data."""

from __future__ import annotations

import json
import logging
import requests
from bot.config import HF_TOKEN, HF_API_URL, ANALYST_MODEL

logger = logging.getLogger(__name__)

GRETA_PROMPT = """You are Greta, a brutally honest environmental impact analyst. You judge clothing based on its environmental footprint.

Here is the garment data:

Garment: {garment_type}
Materials: {materials}
Weight: {weight}g
Country of origin: {country}

CO2 footprint: {co2_total} kg CO2e
Water usage: {water_total} liters
Cutting waste: {cutting_waste}%
Production country: {production_country}

Give THREE separate verdicts using traffic light colors:

1. CARBON — based on CO2 emissions
   GREEN: under 5 kg CO2e (low impact, good choice)
   YELLOW: 5-15 kg CO2e (moderate, could be worse)
   RED: over 15 kg CO2e (high carbon footprint, bad)

2. WATER — based on water consumption
   GREEN: under 1,000 liters
   YELLOW: 1,000-5,000 liters
   RED: over 5,000 liters

3. OVERALL — your gut judgment considering everything: materials, production, transport, recyclability
   GREEN: eco-friendly choice
   YELLOW: average, room for improvement
   RED: environmentally harmful

Respond in this EXACT format (keep it punchy and direct, like Greta would say):
CARBON: GREEN/YELLOW/RED
CARBON_COMMENT: one sharp sentence
WATER: GREEN/YELLOW/RED
WATER_COMMENT: one sharp sentence
OVERALL: GREEN/YELLOW/RED
OVERALL_COMMENT: two sentences max. Be direct, factual, and slightly provocative."""


def greta_judge(garment: dict, impact: dict) -> dict:
    """Get Greta's environmental verdict on the garment."""
    co2 = impact["co2"]
    water = impact["water"]
    bom = impact["bom"]
    prod = impact["production"]

    materials_str = ", ".join(
        f"{m['percentage']}% {m['fiber']}" for m in garment.get("materials", [])
    )

    prompt = GRETA_PROMPT.format(
        garment_type=garment.get("garment_type", "unknown"),
        materials=materials_str,
        weight=garment.get("estimated_weight_grams", "?"),
        country=garment.get("country_of_origin", "unknown"),
        co2_total=co2["total_kg_co2e"],
        water_total=water["total_liters"],
        cutting_waste=bom.get("cutting_waste_pct", 15),
        production_country=prod.get("typical_production_country", "unknown"),
    )

    payload = {
        "model": ANALYST_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
    }
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

        result = {
            "carbon": "YELLOW", "carbon_comment": "",
            "water": "YELLOW", "water_comment": "",
            "overall": "YELLOW", "overall_comment": "",
        }

        for line in content.split("\n"):
            stripped = line.strip()
            upper = stripped.upper()

            if upper.startswith("CARBON_COMMENT:"):
                result["carbon_comment"] = stripped.split(":", 1)[1].strip()
            elif upper.startswith("WATER_COMMENT:"):
                result["water_comment"] = stripped.split(":", 1)[1].strip()
            elif upper.startswith("OVERALL_COMMENT:"):
                result["overall_comment"] = stripped.split(":", 1)[1].strip()
            elif upper.startswith("CARBON:"):
                v = upper.split(":", 1)[1].strip()
                if "GREEN" in v:
                    result["carbon"] = "GREEN"
                elif "RED" in v:
                    result["carbon"] = "RED"
                else:
                    result["carbon"] = "YELLOW"
            elif upper.startswith("WATER:"):
                v = upper.split(":", 1)[1].strip()
                if "GREEN" in v:
                    result["water"] = "GREEN"
                elif "RED" in v:
                    result["water"] = "RED"
                else:
                    result["water"] = "YELLOW"
            elif upper.startswith("OVERALL:"):
                v = upper.split(":", 1)[1].strip()
                if "GREEN" in v:
                    result["overall"] = "GREEN"
                elif "RED" in v:
                    result["overall"] = "RED"
                else:
                    result["overall"] = "YELLOW"

        return result

    except Exception as e:
        logger.error("Greta judge failed: %s", e)
        # Fallback: use thresholds directly
        co2_val = co2["total_kg_co2e"]
        water_val = water["total_liters"]
        return {
            "carbon": "GREEN" if co2_val < 5 else ("YELLOW" if co2_val < 15 else "RED"),
            "carbon_comment": f"{co2_val} kg CO2e for a single garment.",
            "water": "GREEN" if water_val < 1000 else ("YELLOW" if water_val < 5000 else "RED"),
            "water_comment": f"{water_val:,} liters of water used.",
            "overall": "GREEN" if co2_val < 5 and water_val < 1000 else ("RED" if co2_val > 15 or water_val > 5000 else "YELLOW"),
            "overall_comment": "LLM analysis unavailable. Verdict based on thresholds.",
        }
