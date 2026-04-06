"""AI Vision: identify garments and read labels from photos."""

from __future__ import annotations

import base64
import json
import logging
import time
import requests
from bot.config import HF_TOKEN, HF_API_URL, VISION_MODEL

logger = logging.getLogger(__name__)

VISION_MODELS = [
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    VISION_MODEL,
    "Qwen/Qwen3-VL-8B-Instruct",
    "google/gemma-3-27b-it",
]

# First: classify what the image is
CLASSIFY_PROMPT = """Look at this image and classify it as ONE of:
- "garment" — a full clothing item (shirt, jacket, dress, etc.)
- "label" — a care/composition label on clothing (showing materials, wash instructions, country)
- "other" — not clothing related

Return ONLY valid JSON:
{"image_type": "garment|label|other", "brief": "short description"}"""

GARMENT_PROMPT = """You are a textile and garment identification expert. Analyze this clothing image.

Identify ALL of the following from what you can see:

1. GARMENT TYPE: Be specific (e.g., "crew neck t-shirt", "slim fit jeans", "puffer jacket")
2. MATERIALS: Estimate the fabric composition (e.g., "100% cotton", "65% polyester 35% cotton")
   Use visual cues: sheen = polyester/nylon, matte = cotton, fuzzy = wool, stretchy = elastane
3. FABRIC: Construction type (woven, knit, denim, fleece) and estimated weight (GSM)
4. TRIMS: Buttons, zippers, labels, elastic, rivets
5. COLOR/FINISH: Color and treatment (washed, printed, embroidered, garment-dyed)
6. SIZE CATEGORY: XS/S/M/L/XL/XXL
7. CONSTRUCTION: basic (t-shirt), moderate (jeans, button-up), complex (tailored jacket)

Return ONLY valid JSON:
{
  "garment_type": "crew neck t-shirt",
  "garment_category": "tshirt",
  "materials": [{"fiber": "cotton", "percentage": 100}],
  "fabric_type": "jersey knit",
  "fabric_weight_gsm": 180,
  "color": "navy blue",
  "finish": "garment-dyed",
  "trims": ["neck label", "hem label"],
  "construction_complexity": "basic",
  "size_category": "M",
  "estimated_weight_grams": 200,
  "confidence": "high",
  "notes": ""
}

For garment_category use: tshirt, shirt, jeans, trousers, dress, skirt, jacket, coat, hoodie, sweater, shorts, underwear, socks, activewear, suit
If NOT a garment, set confidence to "none"."""

LABEL_PROMPT = """You are reading a clothing care/composition label. Extract ALL text you can see.

Focus on:
1. MATERIALS/COMPOSITION: exact fiber percentages (e.g., "65% Polyester, 35% Cotton")
2. COUNTRY OF ORIGIN: "Made in China", "Made in Italy", etc.
3. BRAND: if visible
4. CARE INSTRUCTIONS: wash temperature, dry clean, iron settings
5. SIZE: if shown on label

RULES:
- Read the EXACT text — do not guess percentages
- If multiple materials listed, include ALL with exact percentages
- If you see care symbols (icons), describe them

Return ONLY valid JSON:
{
  "materials": [
    {"fiber": "polyester", "percentage": 65},
    {"fiber": "cotton", "percentage": 35}
  ],
  "country_of_origin": "China",
  "brand": "",
  "size": "M",
  "care_instructions": ["Machine wash 30°C", "Do not bleach", "Tumble dry low", "Iron low"],
  "confidence": "high",
  "raw_text": "the full text you can read on the label"
}
If NOT a label, set confidence to "none"."""


def _call_vision(image_bytes: bytes, media_type: str, prompt: str) -> dict | None:
    """Send image to vision model with given prompt."""
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    for model in VISION_MODELS:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_base64}"}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "max_tokens": 500,
        }

        for attempt in range(2):
            try:
                logger.info("Vision attempt %d with model %s", attempt + 1, model)
                response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=90)
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()

                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    content = content.rsplit("```", 1)[0]

                return json.loads(content)
            except requests.RequestException as e:
                logger.warning("Vision API failed (model=%s, attempt=%d): %s", model, attempt + 1, e)
                if attempt == 0:
                    time.sleep(2)
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.error("Failed to parse vision response (model=%s): %s", model, e)
                break

    logger.error("All vision models failed")
    return None


def classify_image(image_bytes: bytes, media_type: str = "image/jpeg") -> dict | None:
    """Classify whether image is a garment, label, or other."""
    return _call_vision(image_bytes, media_type, CLASSIFY_PROMPT)


def identify_garment(image_bytes: bytes, media_type: str = "image/jpeg") -> dict | None:
    """Identify garment details from photo."""
    return _call_vision(image_bytes, media_type, GARMENT_PROMPT)


def read_label(image_bytes: bytes, media_type: str = "image/jpeg") -> dict | None:
    """Read composition/care label from photo."""
    return _call_vision(image_bytes, media_type, LABEL_PROMPT)
