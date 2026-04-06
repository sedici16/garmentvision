# GarmentScan

A Telegram bot that analyzes clothing photos to calculate environmental impact, production data, and material composition. Snap a photo, get the full footprint.

## Who Is This For

- **Fashion brands & designers** — estimate BOM, production cost, and environmental impact from a sample photo before sourcing
- **Sustainability teams** — quick CO2/water audits without waiting for full lifecycle assessment reports
- **EU compliance** — the EU Digital Product Passport (mandatory 2027) requires CO2, water, and material disclosure per garment. This gives you a first estimate instantly
- **Fashion students** — learn garment construction, materials, and environmental impact visually
- **Conscious consumers** — scan clothes while shopping to understand the real environmental cost

## How It Works

1. Send a photo of a clothing item to the Telegram bot
2. Optionally send a photo of the care/composition label for exact materials
3. Get back: full environmental report with CO2, water, BOM, production data, and Greta Mode verdict

### Pipeline

```
Photo --> Classify (AI Vision) --> Is it a garment or a label?
                |                            |
          GARMENT                        LABEL
                |                            |
    Identify type, fabric,          Read exact materials %,
    weight, trims, color            country, care instructions
                |                            |
                +------ MERGE DATA ----------+
                             |
                   Calculate Impact (local data)
                   ├── CO2 footprint
                   ├── Water usage
                   ├── Bill of Materials
                   └── Production estimate
                             |
                   Ecobalyse API (EU PEF enrichment)
                             |
                   Greta Mode (LLM judgment)
                   ├── Carbon:  GREEN / YELLOW / RED
                   ├── Water:   GREEN / YELLOW / RED
                   └── Overall: GREEN / YELLOW / RED
                             |
                   Full Report --> User
```

### Two-Step Flow

**Garment photo first:**
1. Send garment photo → bot identifies type, estimates materials
2. Bot asks: "Want to add a label photo for exact materials?"
3. Send up to 2 label photos → exact composition extracted
4. Full report generated

**Label photo first:**
1. Send label photo → bot reads exact materials, country of origin
2. Bot asks: "Now send the garment photo"
3. Send garment photo → type and construction identified
4. Full report generated with exact label data

## Data Sources

All environmental data comes from published, peer-reviewed, or government sources:

| Source | Data Used | Type |
|--------|-----------|------|
| **WRAP / Carbon Trust** (UK govt) | CO2 emissions per fiber type (kg CO2e/kg), production stage breakdown % | Local lookup table |
| **Carbonfact** | CO2 per finished garment for 30+ garment types | Local lookup table |
| **Water Footprint Network** | Water consumption per fiber type (liters/kg) | Local lookup table |
| **Industry BOM specs** | Fabric weight, GSM, thread consumption, trim specs per garment type | Local lookup table |
| **PMC academic studies** | Energy consumption per production stage (MJ/kg) | Local lookup table |
| **Ecobalyse** (French govt) | EU Product Environmental Footprint (PEF) scores | API call |
| **OEcotextiles** | Embodied energy per fiber, carbon footprint of fabric | Local lookup table |

The full compiled dataset is in `data/environmental_data.py` (718 lines, fully cited).

## What Is Calculated vs What Is Estimated

### Calculated from data (deterministic, math only)

These use lookup tables × inputs from the vision model. No LLM involved.

| Output | Formula | Source |
|--------|---------|--------|
| CO2 per fiber | `CO2_per_kg[fiber] × weight_kg × percentage` | WRAP table |
| CO2 per garment | Direct lookup by garment category | Carbonfact table |
| CO2 stage breakdown | `total_CO2 × stage_percentage` (dyeing 36%, yarn 28%, fiber 15%, fabric 12%, assembly 7%, distribution 1%) | WRAP |
| CO2 transport | `weight_kg × 0.5` (sea freight Asia→EU) | Industry estimate |
| Water per fiber | `liters_per_kg[fiber] × weight_kg × percentage` | Water Footprint Network |
| Water dyeing | `150 liters/kg × weight_kg` | Industry average |
| BOM components | Template lookup by garment category (fabric, thread, trims) | Industry specs |
| Fabric area | `fabric_weight_grams / GSM` | Math |
| Thread estimate | By complexity: basic=100m, moderate=180m, complex=300m | Industry specs |
| Sewing time | By complexity: basic=15min, moderate=30min, complex=56min | Industry specs |
| CMT cost | `hourly_rate × (time / 60)` | Industry rates |
| Equivalents | `CO2 / 0.21` = km driven, `water / 65` = showers | Fixed constants |

### Estimated by Vision AI (from photo)

The vision model (Qwen2.5-VL-72B) analyzes the photo and estimates these inputs. These feed into the calculations above.

| Input | How It's Estimated | Confidence |
|-------|-------------------|------------|
| Garment type | Visual identification (shape, style) | High |
| Materials | Visual cues: sheen=polyester, matte=cotton, fuzzy=wool | **Low — biggest uncertainty** |
| Fabric weight (GSM) | Estimated from apparent thickness/drape | Medium |
| Total weight (grams) | Estimated from garment type and size | Medium |
| Color/finish | Direct visual observation | High |
| Trims | Visual detection of buttons, zippers, rivets | High |
| Construction complexity | Judged as basic/moderate/complex | Medium |
| Size | Estimated from proportions | Medium |

**The label photo eliminates the biggest uncertainty** — materials go from "guessed from appearance" to "exact percentages read from the label". This significantly improves CO2 and water accuracy.

### Estimated by Label Reading (from label photo)

When the user sends a label photo, the vision model reads:

| Field | Accuracy |
|-------|----------|
| Material composition (e.g., "65% Polyester, 35% Cotton") | High — exact text reading |
| Country of origin ("Made in Bangladesh") | High |
| Care instructions | High |
| Brand | High |
| Size | High |

### Judged by LLM (Greta Mode)

All calculated data is sent to a 72B language model for environmental judgment. The LLM does NOT calculate — it reads the numbers and gives verdicts.

| Verdict | Thresholds | LLM Role |
|---------|-----------|----------|
| Carbon: GREEN | < 5 kg CO2e | Read CO2 number, give verdict + sharp comment |
| Carbon: YELLOW | 5-15 kg CO2e | |
| Carbon: RED | > 15 kg CO2e | |
| Water: GREEN | < 1,000 liters | Read water number, give verdict + comment |
| Water: YELLOW | 1,000-5,000 liters | |
| Water: RED | > 5,000 liters | |
| Overall | Holistic | Judge everything: materials, production, transport, recyclability |

## Example Response

```
👕 Crew neck t-shirt
🧵 100% cotton (estimated)
⚖️ ~200g · jersey knit · 180 GSM
🎨 navy blue · garment-dyed

🌍 CO2 Footprint: 5.7 kg CO2e
   Dyeing Finishing: 2.05 kg
   Yarn Production: 1.60 kg
   Fiber Production: 0.86 kg
   Fabric Production: 0.68 kg
   Assembly Cut Sew: 0.40 kg
   Transport: 0.10 kg
   = 27.1 km driven
   = 713 phone charges

💧 Water: 1,814 liters
   Cotton: 1,784 L
   Dyeing: 30 L
   = 27 showers

📋 Bill of Materials:
   Fabric (cotton): 170g (100%)
   Sewing thread: ~100m (4g)
   Care/brand labels: 2 pcs (3g)
   Packaging (polybag + tag): 1 set (15g)
   Cutting waste: ~15%
   Fabric area: 0.94 m²

🏭 Production:
   Total time: 15 min
   Cutting: 2 min
   Sewing: 8 min
   Finishing: 3 min
   Qc Packing: 2 min
   CMT cost: $0.88
   Machines: single needle lockstitch, overlock
   Typical origin: Bangladesh, Vietnam, Cambodia
   Min order: 500 pcs

━━━━━━━━━━━━━━━━━━━━━━
🌱 GRETA MODE

🟡 Carbon: YELLOW
   5.7 kg CO2e — moderate, but cotton farming is thirsty work.
🟡 Water: YELLOW
   1,814 liters for a single t-shirt. That's 27 showers.
🟡 Overall: YELLOW
   Conventional cotton is the fast fashion default. Switch to
   organic cotton and you halve the water footprint instantly.
```

## Models Used

| Role | Model | Provider |
|------|-------|----------|
| Image classification | Qwen2.5-VL-72B-Instruct | HF Inference API (free) |
| Garment identification | Qwen2.5-VL-72B-Instruct | HF Inference API (free) |
| Label reading | Qwen2.5-VL-72B-Instruct | HF Inference API (free) |
| Greta Mode (judgment) | Qwen2.5-72B-Instruct | HF Inference API (free) |

Fallback vision models: Llama-4-Scout-17B, Qwen2.5-VL-7B, Qwen3-VL-8B, Gemma-3-27B.

All models run via HuggingFace free inference tier. No GPU required.

## Setup

### Requirements

- Python 3.9+
- Telegram bot token (from [@BotFather](https://t.me/BotFather))
- HuggingFace API token (free tier works)

### Install

```bash
git clone https://github.com/sedici16/garmentvision.git
cd garmentvision
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
```

Fill in your keys:
```
TELEGRAM_BOT_TOKEN=your-bot-token
hf=your-huggingface-token
```

### Run

```bash
python -m bot.main
```

Dashboard available at `http://localhost:5002`

## Project Structure

```
garmentvision/
├── bot/
│   ├── main.py           # Entry point, handler registration
│   ├── config.py         # Environment variables
│   ├── handlers.py       # Telegram handlers, two-step flow, session state
│   ├── vision.py         # AI vision: classify, identify garment, read label
│   ├── calculator.py     # Environmental impact calculations (local data)
│   ├── ecobalyse.py      # Ecobalyse API client (EU PEF scores)
│   ├── greta.py          # Greta Mode: LLM environmental judgment
│   ├── db.py             # SQLite analytics
│   └── dashboard.py      # Flask web dashboard
├── data/
│   └── environmental_data.py  # 718 lines of compiled environmental data
├── templates/
│   ├── dashboard.html
│   └── user_dashboard.html
├── .env.example
├── requirements.txt
└── README.md
```

## License

MIT
