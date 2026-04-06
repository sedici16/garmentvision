"""Ecobalyse API client — French government textile environmental impact API."""

from __future__ import annotations

import logging
import requests

logger = logging.getLogger(__name__)

ECOBALYSE_API = "https://ecobalyse.beta.gouv.fr/api"

# Ecobalyse material IDs
MATERIAL_MAP = {
    "cotton": "ei-coton",
    "polyester": "ei-pet",
    "wool": "ei-laine-nouvelle-zelande",
    "nylon": "ei-pa",
    "linen": "ei-lin",
    "silk": "ei-soie",
    "viscose": "ei-viscose",
    "elastane": "ei-elasthane",
    "acrylic": "ei-acrylique",
    "hemp": "ei-chanvre",
}

# Ecobalyse product categories
PRODUCT_MAP = {
    "tshirt": "tshirt",
    "shirt": "chemise",
    "jeans": "jean",
    "trousers": "pantalon",
    "dress": "robe",
    "skirt": "jupe",
    "jacket": "manteau",
    "coat": "manteau",
    "hoodie": "pull",
    "sweater": "pull",
    "shorts": "short",
}


def query_ecobalyse(garment: dict) -> dict | None:
    """Query Ecobalyse API for detailed environmental impact.
    Returns None if API is unavailable or garment type unsupported."""
    category = garment.get("garment_category", "tshirt")
    materials = garment.get("materials", [{"fiber": "cotton", "percentage": 100}])
    weight_g = garment.get("estimated_weight_grams", 200)

    product = PRODUCT_MAP.get(category)
    if not product:
        return None

    # Build materials list for API
    api_materials = []
    for mat in materials:
        fiber = mat.get("fiber", "cotton").lower()
        eco_id = MATERIAL_MAP.get(fiber)
        if not eco_id:
            eco_id = "ei-coton"  # default to cotton
        api_materials.append({
            "id": eco_id,
            "share": mat.get("percentage", 100) / 100,
            "country": "CN",  # assume China production
        })

    params = {
        "mass": weight_g / 1000,
        "product": product,
        "materials": api_materials,
        "countryFabric": "CN",
        "countryDyeing": "CN",
        "countryMaking": "CN",
    }

    try:
        resp = requests.post(
            f"{ECOBALYSE_API}/textile/simulator/detailed",
            json=params,
            timeout=15,
            headers={"Accept": "application/json"},
        )
        if resp.status_code == 200:
            data = resp.json()
            return _parse_ecobalyse_response(data)
        else:
            logger.warning("Ecobalyse API returned %d: %s", resp.status_code, resp.text[:200])
            return None
    except Exception as e:
        logger.warning("Ecobalyse API failed: %s", e)
        return None


def _parse_ecobalyse_response(data: dict) -> dict:
    """Parse Ecobalyse response into a simplified format."""
    impacts = data.get("impacts", {})
    stages = data.get("lifeCycle", [])

    result = {
        "climate_change_kg": impacts.get("cch"),
        "water_use_m3": impacts.get("swe"),
        "eutrophication_kg": impacts.get("fwe"),
        "resource_depletion_mj": impacts.get("adr"),
        "pef_score": impacts.get("pef"),
        "stages": [],
    }

    for stage in stages:
        result["stages"].append({
            "name": stage.get("label", ""),
            "climate_change": stage.get("impacts", {}).get("cch"),
            "water_use": stage.get("impacts", {}).get("swe"),
        })

    return result
