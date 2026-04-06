"""Calculate environmental impact from garment identification data using local datasets."""

from __future__ import annotations

import logging
import sys
import os

# Add project root to path for data imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.environmental_data import (
    CO2_PER_KG_FIBER,
    CO2_PER_GARMENT_CARBONFACT,
    CO2_STAGE_BREAKDOWN_PERCENT,
    WATER_PER_KG_FIBER,
    WATER_PER_GARMENT,
    WATER_DYEING_FINISHING,
    GARMENT_BOM,
)

logger = logging.getLogger(__name__)

# Mapping from vision categories to GARMENT_BOM keys
CATEGORY_TO_BOM = {
    "tshirt": "t_shirt",
    "shirt": "dress_shirt",
    "jeans": "jeans",
    "trousers": "trousers_chinos",
    "dress": "dress",
    "skirt": "dress",
    "jacket": "jacket_coat",
    "coat": "jacket_coat",
    "hoodie": "hoodie",
    "sweater": "sweater_pullover",
    "shorts": "trousers_chinos",
    "underwear": "underwear_boxers",
    "socks": "socks_pair",
    "activewear": "t_shirt",
    "suit": "jacket_coat",
}

# Carbonfact category mapping
CATEGORY_TO_CARBONFACT = {
    "tshirt": "tshirt",
    "shirt": "shirt",
    "jeans": "jeans",
    "trousers": "trousers",
    "dress": "dress",
    "skirt": "skirt",
    "jacket": "jacket",
    "coat": "coat",
    "hoodie": "hoodie",
    "sweater": "sweater",
    "shorts": "shorts",
    "underwear": "underwear",
    "socks": "socks",
    "activewear": "sportswear",
    "suit": "suit",
}


def calculate_impact(garment: dict) -> dict:
    """Calculate full environmental impact from vision-identified garment data."""
    category = garment.get("garment_category", "tshirt")
    materials = garment.get("materials", [{"fiber": "cotton", "percentage": 100}])
    weight_g = garment.get("estimated_weight_grams", 200)
    weight_kg = weight_g / 1000.0

    # --- BOM ---
    bom_key = CATEGORY_TO_BOM.get(category, "tshirt_basic")
    bom_template = GARMENT_BOM.get(bom_key, GARMENT_BOM.get("tshirt_basic", {}))
    bom = _build_bom(bom_template, garment, weight_g)

    # --- CO2 ---
    co2 = _calculate_co2(category, materials, weight_kg)

    # --- Water ---
    water = _calculate_water(category, materials, weight_kg)

    # --- Production data ---
    production = _estimate_production(category, garment)

    return {
        "bom": bom,
        "co2": co2,
        "water": water,
        "production": production,
    }


def _build_bom(template: dict, garment: dict, weight_g: float) -> dict:
    """Build Bill of Materials from template and garment data."""
    materials = garment.get("materials", [{"fiber": "cotton", "percentage": 100}])
    trims = garment.get("trims", [])
    fabric_gsm = garment.get("fabric_weight_gsm") or template.get("fabric_gsm", 180)

    # Fabric area estimation
    fabric_weight_g = weight_g * 0.85  # ~85% is fabric
    fabric_area_sqm = fabric_weight_g / fabric_gsm if fabric_gsm else 1.0

    # Thread estimation based on complexity
    complexity = garment.get("construction_complexity", "basic")
    thread_m = {"basic": 100, "moderate": 180, "complex": 300}.get(complexity, 150)

    bom_items = []

    # Fabric
    for mat in materials:
        fiber = mat.get("fiber", "cotton")
        pct = mat.get("percentage", 100)
        mat_weight = fabric_weight_g * (pct / 100)
        bom_items.append({
            "component": f"Fabric ({fiber})",
            "material": fiber,
            "quantity": f"{mat_weight:.0f}g ({pct}%)",
            "weight_g": round(mat_weight),
        })

    # Thread
    bom_items.append({
        "component": "Sewing thread",
        "material": "polyester",
        "quantity": f"~{thread_m}m",
        "weight_g": round(thread_m * 0.04),  # ~0.04g per meter
    })

    # Trims from vision
    trim_weight = 0
    for trim in trims:
        trim_lower = trim.lower()
        if "button" in trim_lower:
            bom_items.append({"component": "Buttons", "material": "plastic/metal", "quantity": "4-6 pcs", "weight_g": 8})
            trim_weight += 8
        elif "zipper" in trim_lower or "zip" in trim_lower:
            bom_items.append({"component": "Zipper", "material": "metal/plastic", "quantity": "1 pc", "weight_g": 25})
            trim_weight += 25
        elif "rivet" in trim_lower:
            bom_items.append({"component": "Rivets", "material": "metal", "quantity": "5-6 pcs", "weight_g": 15})
            trim_weight += 15
        elif "elastic" in trim_lower:
            bom_items.append({"component": "Elastic band", "material": "rubber/polyester", "quantity": "~50cm", "weight_g": 5})
            trim_weight += 5
        elif "label" in trim_lower:
            bom_items.append({"component": "Labels", "material": "polyester/paper", "quantity": "1-2 pcs", "weight_g": 2})
            trim_weight += 2

    # Always add labels if not detected
    if not any("label" in t.lower() for t in trims):
        bom_items.append({"component": "Care/brand labels", "material": "polyester", "quantity": "2 pcs", "weight_g": 3})
        trim_weight += 3

    # Packaging
    bom_items.append({"component": "Packaging (polybag + tag)", "material": "LDPE/cardboard", "quantity": "1 set", "weight_g": 15})

    return {
        "items": bom_items,
        "total_weight_g": weight_g,
        "fabric_weight_g": round(fabric_weight_g),
        "fabric_area_sqm": round(fabric_area_sqm, 2),
        "fabric_gsm": fabric_gsm,
        "cutting_waste_pct": template.get("cutting_waste_pct", 15),
    }


def _calculate_co2(category: str, materials: list, weight_kg: float) -> dict:
    """Calculate CO2 emissions breakdown."""
    # Try Carbonfact per-garment data first
    cf_key = CATEGORY_TO_CARBONFACT.get(category, "tshirt")
    cf_data = CO2_PER_GARMENT_CARBONFACT.get(cf_key)
    if cf_data:
        total_garment = cf_data["kg_co2e"]
    else:
        total_garment = None

    # Calculate from fiber data
    fiber_co2 = 0
    fiber_breakdown = []
    for mat in materials:
        fiber = mat.get("fiber", "cotton").lower()
        pct = mat.get("percentage", 100) / 100
        fiber_data = CO2_PER_KG_FIBER.get(fiber, CO2_PER_KG_FIBER.get("cotton"))
        co2_per_kg = fiber_data["kg_co2e_per_kg"] if fiber_data else 28.0
        mat_co2 = co2_per_kg * weight_kg * pct
        fiber_co2 += mat_co2
        fiber_breakdown.append({
            "fiber": fiber,
            "percentage": int(pct * 100),
            "co2_per_kg": co2_per_kg,
            "co2_total": round(mat_co2, 2),
        })

    # Use Carbonfact total if available, otherwise estimate from fiber
    total = total_garment if total_garment else round(fiber_co2, 2)

    # Stage breakdown
    stages = {}
    for stage, pct in CO2_STAGE_BREAKDOWN_PERCENT.items():
        if stage == "source":
            continue
        stages[stage] = round(total * pct, 2)

    # Transport estimate (assume Asia to EU)
    transport_co2 = round(weight_kg * 0.5, 2)  # ~0.5 kg CO2e/kg for sea freight

    return {
        "total_kg_co2e": round(total + transport_co2, 2),
        "fiber_breakdown": fiber_breakdown,
        "stage_breakdown": stages,
        "transport_co2": transport_co2,
        "carbonfact_reference": total_garment,
        "equivalent_km_driven": round((total + transport_co2) / 0.21, 1),  # avg car ~0.21 kg/km
        "equivalent_phone_charges": round((total + transport_co2) / 0.008),  # ~8g CO2 per charge
    }


def _calculate_water(category: str, materials: list, weight_kg: float) -> dict:
    """Calculate water consumption."""
    # Per-garment reference
    water_ref = WATER_PER_GARMENT.get(category)
    ref_liters = water_ref["liters"] if water_ref else None

    # Calculate from fiber data
    fiber_water = 0
    fiber_breakdown = []
    for mat in materials:
        fiber = mat.get("fiber", "cotton").lower()
        pct = mat.get("percentage", 100) / 100
        water_key = f"{fiber}_global_avg"
        water_data = WATER_PER_KG_FIBER.get(water_key, WATER_PER_KG_FIBER.get(fiber))
        liters_per_kg = water_data["liters_per_kg"] if water_data else 5000
        mat_water = liters_per_kg * weight_kg * pct
        fiber_water += mat_water
        fiber_breakdown.append({
            "fiber": fiber,
            "liters_per_kg": liters_per_kg,
            "liters_total": round(mat_water),
        })

    # Dyeing water
    dyeing_water = WATER_DYEING_FINISHING.get("typical_range_per_kg", {})
    dye_liters = 150 * weight_kg  # mid-range estimate

    total = round(fiber_water + dye_liters)

    return {
        "total_liters": total,
        "fiber_breakdown": fiber_breakdown,
        "dyeing_liters": round(dye_liters),
        "reference_per_garment": ref_liters,
        "equivalent_showers": round(total / 65),  # avg shower ~65L
        "equivalent_drinking_days": round(total / 2),  # ~2L per day
    }


def _estimate_production(category: str, garment: dict) -> dict:
    """Estimate production parameters."""
    complexity = garment.get("construction_complexity", "basic")

    # Sewing time (minutes) by complexity
    sew_times = {
        "basic": {"cutting": 2, "sewing": 8, "finishing": 3, "qc_packing": 2},
        "moderate": {"cutting": 4, "sewing": 18, "finishing": 5, "qc_packing": 3},
        "complex": {"cutting": 6, "sewing": 35, "finishing": 10, "qc_packing": 5},
    }
    times = sew_times.get(complexity, sew_times["moderate"])
    total_minutes = sum(times.values())

    # Machines needed
    machines = {
        "basic": ["single needle lockstitch", "overlock"],
        "moderate": ["single needle lockstitch", "overlock", "bartack", "buttonhole"],
        "complex": ["single needle lockstitch", "overlock", "bartack", "buttonhole", "blind hem", "pressing"],
    }

    # Cost estimate (CMT - Cut Make Trim)
    labor_cost_per_hour = {"basic": 3.5, "moderate": 4.5, "complex": 6.0}
    hourly = labor_cost_per_hour.get(complexity, 4.5)
    cmt_cost = round(hourly * (total_minutes / 60), 2)

    # Typical production country
    countries = {
        "basic": "Bangladesh, Vietnam, Cambodia",
        "moderate": "China, India, Turkey",
        "complex": "Italy, Portugal, Romania",
    }

    return {
        "time_breakdown_minutes": times,
        "total_time_minutes": total_minutes,
        "machines_required": machines.get(complexity, machines["moderate"]),
        "cmt_cost_usd": cmt_cost,
        "labor_cost_per_hour_usd": hourly,
        "typical_production_country": countries.get(complexity, "China, India"),
        "minimum_order_qty": {"basic": 500, "moderate": 300, "complex": 100}.get(complexity, 300),
    }
