"""
Garment Environmental Impact & Production Cost Data
=====================================================

Compiled from multiple FREE, open sources. All values include source citations.
See SOURCES dict at bottom for full references.

Data last compiled: 2026-04-05
"""

# =============================================================================
# 1. CO2 EMISSIONS PER FIBER TYPE (kg CO2e per kg of fiber/fabric)
# =============================================================================

# Source: WRAP 2012 (via Ethical Consumer), OEcotextiles, 8BillionTrees, PMC studies
# These are CRADLE-TO-GATE values (raw material through fabric production)
CO2_PER_KG_FIBER = {
    # Fiber type: {value, unit, scope, source}
    "wool":       {"kg_co2e_per_kg": 46.0,  "source": "WRAP_2012"},
    "acrylic":    {"kg_co2e_per_kg": 38.0,  "source": "WRAP_2012"},
    "viscose":    {"kg_co2e_per_kg": 30.0,  "source": "WRAP_2012"},
    "cotton":     {"kg_co2e_per_kg": 28.0,  "source": "WRAP_2012"},
    "silk":       {"kg_co2e_per_kg": 25.0,  "source": "WRAP_2012"},
    "polyester":  {"kg_co2e_per_kg": 21.0,  "source": "WRAP_2012"},
    "polyurethane": {"kg_co2e_per_kg": 20.0, "source": "WRAP_2012"},
    "linen":      {"kg_co2e_per_kg": 15.0,  "source": "WRAP_2012"},
}

# Alternative dataset: per 2 sq meters of 150gsm fabric (0.3 kg)
# Source: "A Carbon Footprint for UK Clothing" (WRAP/Carbon Trust, Table 21)
CO2_PER_2SQM_150GSM = {
    "wool":     {"kg_co2e": 13.89, "source": "WRAP_UK_CLOTHING"},
    "acrylic":  {"kg_co2e": 11.53, "source": "WRAP_UK_CLOTHING"},
    "cotton":   {"kg_co2e":  8.30, "source": "WRAP_UK_CLOTHING"},
    "silk":     {"kg_co2e":  7.63, "source": "WRAP_UK_CLOTHING"},
    "nylon":    {"kg_co2e":  7.31, "source": "WRAP_UK_CLOTHING"},
    "polyester": {"kg_co2e": 6.40, "source": "WRAP_UK_CLOTHING"},
    "linen":    {"kg_co2e":  4.50, "source": "WRAP_UK_CLOTHING"},
}

# Raw material extraction ONLY (fiber production stage, before spinning)
# Source: OEcotextiles blog (citing Stockholm Environment Institute data)
CO2_FIBER_PRODUCTION_ONLY = {
    # kg CO2e per metric ton of spun fiber
    "polyester_usa":         {"crop": 0.0,  "fiber_prod": 9.52, "total": 9.52,  "unit": "tonnes_co2e_per_tonne"},
    "cotton_conventional_us": {"crop": 4.20, "fiber_prod": 1.70, "total": 5.90, "unit": "tonnes_co2e_per_tonne"},
    "hemp_conventional":      {"crop": 1.90, "fiber_prod": 2.15, "total": 4.05, "unit": "tonnes_co2e_per_tonne"},
    "cotton_organic_india":   {"crop": 2.00, "fiber_prod": 1.80, "total": 3.80, "unit": "tonnes_co2e_per_tonne"},
    "cotton_organic_usa":     {"crop": 0.90, "fiber_prod": 1.45, "total": 2.35, "unit": "tonnes_co2e_per_tonne"},
}

# More granular per-kg values from multiple academic sources
CO2_PER_KG_FIBER_DETAILED = {
    "virgin_polyester":    {"kg_co2e_per_kg": 10.2,   "source": "8BILLIONTREES"},
    "recycled_polyester":  {"kg_co2e_per_kg":  0.201, "source": "8BILLIONTREES"},
    "cotton_conventional": {"kg_co2e_per_kg":  9.3,   "source": "8BILLIONTREES"},
    "cotton_organic":      {"kg_co2e_per_kg":  6.5,   "source": "8BILLIONTREES"},
    "virgin_nylon":        {"kg_co2e_per_kg":  6.52,  "source": "8BILLIONTREES"},
    "recycled_nylon":      {"kg_co2e_per_kg":  0.201, "source": "8BILLIONTREES"},
    "polyester_alt":       {"kg_co2e_per_kg":  9.52,  "source": "OECOTEXTILES"},
    "cotton_conv_alt":     {"kg_co2e_per_kg":  5.89,  "source": "OECOTEXTILES"},
    "polyester_traded":    {"kg_co2e_per_kg":  2.30,  "source": "HEMPFOUNDATION"},  # 2,300 kg/tonne
}


# =============================================================================
# 2. CO2 BREAKDOWN BY PRODUCTION STAGE
# =============================================================================

# Source: Ethical Consumer / WRAP - % of total garment emissions by stage
CO2_STAGE_BREAKDOWN_PERCENT = {
    "dyeing_finishing":  0.36,
    "yarn_production":   0.28,
    "fiber_production":  0.15,
    "fabric_production": 0.12,
    "assembly_cut_sew":  0.07,
    "distribution":      0.01,
    "source": "WRAP_2012",
}

# Source: PMC/Heliyon study - Pakistan textile sector (FY2021-22)
# Specific energy consumption by process stage
ENERGY_PER_STAGE = {
    "spinning":   {"mj_per_kg": 30.795,  "unit": "MJ/kg yarn",     "source": "PMC_HELIYON"},
    "weaving":    {"mj_per_sqm": 8.495,  "unit": "MJ/sq.m fabric", "source": "PMC_HELIYON"},
    "processing": {"mj_per_sqm": 7.598,  "unit": "MJ/sq.m fabric", "source": "PMC_HELIYON"},
    "knitting":   {"mj_per_sqm": 11.098, "unit": "MJ/sq.m fabric", "source": "PMC_HELIYON"},
    "garmenting": {"mj_per_sqm": 7.444,  "unit": "MJ/sq.m fabric", "source": "PMC_HELIYON"},
}

# Embodied energy in fiber production (MJ per kg)
# Source: OEcotextiles (citing various LCA studies)
EMBODIED_ENERGY_MJ_PER_KG = {
    "flax":          10,
    "cotton":        55,
    "wool":          63,
    "viscose":      100,
    "polypropylene": 115,
    "polyester":    125,
    "acrylic":      175,
    "nylon":        250,
    "source": "OECOTEXTILES",
}

# Denim jeans lifecycle CO2 breakdown (kg CO2e per pair)
# Source: PMC/Heliyon study
DENIM_JEANS_CO2_BREAKDOWN = {
    "spinning":      {"kg_co2e": 0.84,  "percent": 0.98},
    "weaving":       {"kg_co2e": 18.80, "percent": 22.00},
    "processing":    {"kg_co2e": 27.80, "percent": 32.53},
    "garmenting":    {"kg_co2e": 17.19, "percent": 20.11},
    "denim_washing": {"kg_co2e": 21.68, "percent": 25.37},
    "total":         {"kg_co2e": 85.47},
    "source": "PMC_HELIYON",
}

# Dyeing/wet processing emission factors
DYEING_EMISSION_FACTORS = {
    "batch_dyeing":      {"kg_co2e_per_kg": 5.15,  "source": "ACADEMIC_LCA"},
    "continuous_dyeing":  {"kg_co2e_per_kg": 1.53, "source": "ACADEMIC_LCA"},
    "cotton_dyeing":      {"kg_co2e_per_kg": 15.63, "source": "ACADEMIC_LCA",
                           "note": "Pure cotton, 1 tonne = 15,627 kg CO2e"},
    "cotton_knit_dyeing": {"kg_co2e_per_kg": 7.51,  "source": "ACADEMIC_LCA"},
    "water_per_kg_dyeing": {"liters_min": 50, "liters_max": 400, "source": "ACADEMIC_LCA"},
}


# =============================================================================
# 3. CO2 PER FINISHED GARMENT TYPE (total lifecycle kg CO2e)
# =============================================================================

# Source: Carbonfact database (comprehensive, PEF-aligned)
CO2_PER_GARMENT_CARBONFACT = {
    # Tops
    "t_shirt":          {"kg_co2e": 10.60, "source": "CARBONFACT"},
    "long_sleeve_tshirt": {"kg_co2e": 9.76, "source": "CARBONFACT"},
    "tank_top":         {"kg_co2e":  6.91, "source": "CARBONFACT"},
    "shirt":            {"kg_co2e": 11.98, "source": "CARBONFACT"},
    "hoodie":           {"kg_co2e": 18.97, "source": "CARBONFACT"},
    "sweater":          {"kg_co2e": 19.05, "source": "CARBONFACT"},
    "cardigan":         {"kg_co2e": 26.85, "source": "CARBONFACT"},
    "fleece_jacket":    {"kg_co2e": 18.00, "source": "CARBONFACT"},
    # Bottoms
    "jeans":            {"kg_co2e": 16.34, "source": "CARBONFACT"},
    "pants":            {"kg_co2e": 27.50, "source": "CARBONFACT"},
    "leggings":         {"kg_co2e":  6.16, "source": "CARBONFACT"},
    "skirt":            {"kg_co2e": 11.15, "source": "CARBONFACT"},
    # Outerwear
    "jacket":           {"kg_co2e": 29.72, "source": "CARBONFACT"},
    "cape_jacket":      {"kg_co2e": 24.74, "source": "CARBONFACT"},
    "gilet":            {"kg_co2e": 20.95, "source": "CARBONFACT"},
    "coveralls":        {"kg_co2e": 33.74, "source": "CARBONFACT"},
    # Dresses
    "dress":            {"kg_co2e": 14.24, "source": "CARBONFACT"},
    # Underwear / Intimate
    "bra":              {"kg_co2e":  4.90, "source": "CARBONFACT"},
    "boxers":           {"kg_co2e":  5.77, "source": "CARBONFACT"},
    "underwear":        {"kg_co2e": 10.71, "source": "CARBONFACT"},
    "swimwear":         {"kg_co2e":  4.90, "source": "CARBONFACT"},
    # Accessories
    "socks":            {"kg_co2e":  1.83, "source": "CARBONFACT"},
    "tights":           {"kg_co2e":  5.91, "source": "CARBONFACT"},
    "scarf":            {"kg_co2e":  8.60, "source": "CARBONFACT"},
    "gloves":           {"kg_co2e":  4.67, "source": "CARBONFACT"},
    "belt":             {"kg_co2e": 11.19, "source": "CARBONFACT"},
    "baseball_cap":     {"kg_co2e":  4.22, "source": "CARBONFACT"},
    "beanie":           {"kg_co2e":  5.15, "source": "CARBONFACT"},
    # Sleepwear
    "pajamas":          {"kg_co2e": 13.48, "source": "CARBONFACT"},
    # Workwear
    "workwear":         {"kg_co2e": 30.06, "source": "CARBONFACT"},
}

# Alternative per-garment values from Carbon Trust
CO2_PER_GARMENT_CARBON_TRUST = {
    "cotton_shirt":      {"kg_co2e": 15.0,  "source": "CARBON_TRUST"},
    "polyester_jacket":  {"kg_co2e": 18.0,  "source": "CARBON_TRUST"},
    "underwear":         {"kg_co2e":  1.9,  "source": "CARBON_TRUST"},
    "cotton_tshirt":     {"kg_co2e":  6.75, "source": "FUTURE_GREEN",
                          "note": "range 2-7 kg commonly cited"},
    "jeans":             {"kg_co2e": 33.4,  "source": "PLANBE",
                          "note": "other estimates: 20 kg (Future.Green)"},
}


# =============================================================================
# 4. WATER CONSUMPTION DATA
# =============================================================================

# Liters of water per kg of fiber produced
WATER_PER_KG_FIBER = {
    "cotton_global_avg": {"liters_per_kg": 8920,   "source": "WATER_FOOTPRINT_NETWORK"},
    "cotton_range":      {"liters_min": 8000, "liters_max": 10000, "source": "MULTIPLE"},
    "cotton_arid":       {"liters_per_kg": 22500,  "source": "FULGAR",
                          "note": "Arid regions like Uzbekistan/Egypt"},
    "polyester":         {"liters_per_kg": 83,     "source": "MULTIPLE",
                          "note": "Direct production water only, excl. energy chain"},
    "viscose":           {"liters_per_kg": 640,    "source": "WATER_FOOTPRINT_NETWORK"},
    "nylon":             {"liters_per_kg": 100,    "source": "MULTIPLE",
                          "note": "Estimates vary widely"},
    "linen":             {"liters_per_kg": 6000,   "source": "MULTIPLE",
                          "note": "Mostly rain-fed, less blue water than cotton"},
    "wool":              {"liters_per_kg": 17000,  "source": "MULTIPLE",
                          "note": "Mostly green water (rain/grazing)"},
}

# Water per finished garment
WATER_PER_GARMENT = {
    "cotton_tshirt":   {"liters": 2700,  "source": "PLANBE",
                        "note": "Equivalent to 2.5 years of drinking water"},
    "pair_of_jeans":   {"liters": 3781,  "source": "PLANBE"},
    "cotton_shirt":    {"liters": 2500,  "source": "MULTIPLE"},
}

# Water in dyeing/finishing per kg of textile
WATER_DYEING_FINISHING = {
    "dyeing_range":   {"liters_min": 50, "liters_max": 400, "unit": "L/kg product"},
    "typical":        {"liters_per_kg": 150, "note": "Industry average for dyeing"},
    "source": "ACADEMIC_LCA",
}


# =============================================================================
# 5. BILL OF MATERIALS (BOM) - Typical Garment Specifications
# =============================================================================

# Garment weights and fabric requirements
# Sources: Industry data, Ecobalyse (French govt), garment manufacturing references
GARMENT_BOM = {
    "t_shirt": {
        "total_weight_g": 180,
        "fabric_weight_g": 165,
        "fabric_gsm": 160,       # grams per square meter
        "fabric_area_sqm": 1.03,  # approx fabric needed
        "thread_meters": 100,
        "trims": {"labels": 2, "neck_tape_m": 0.4},
        "typical_material": "cotton_jersey",
        "making_waste_pct": 15,   # % fabric waste in cutting
        "source": "INDUSTRY_BOM",
    },
    "polo_shirt": {
        "total_weight_g": 220,
        "fabric_weight_g": 200,
        "fabric_gsm": 200,
        "fabric_area_sqm": 1.2,
        "thread_meters": 120,
        "trims": {"buttons": 3, "labels": 2, "neck_tape_m": 0.4},
        "typical_material": "cotton_pique",
        "making_waste_pct": 15,
        "source": "INDUSTRY_BOM",
    },
    "dress_shirt": {
        "total_weight_g": 250,
        "fabric_weight_g": 220,
        "fabric_gsm": 120,
        "fabric_area_sqm": 1.8,
        "thread_meters": 200,     # Coats Group: 150-200m
        "trims": {"buttons": 11, "labels": 2, "collar_stay": 2, "interlining_sqm": 0.15},
        "typical_material": "cotton_poplin",
        "making_waste_pct": 20,
        "source": "ECOBALYSE_COATS",
    },
    "jeans": {
        "total_weight_g": 850,
        "fabric_weight_g": 750,
        "fabric_gsm": 350,       # denim weight
        "fabric_area_sqm": 1.5,
        "thread_meters": 300,
        "trims": {"buttons": 1, "rivets": 6, "zipper_cm": 15,
                  "labels": 3, "back_patch": 1},
        "typical_material": "cotton_denim",
        "making_waste_pct": 22,   # from Ecobalyse
        "source": "ECOBALYSE_INDUSTRY",
    },
    "hoodie": {
        "total_weight_g": 550,
        "fabric_weight_g": 500,
        "fabric_gsm": 280,       # fleece-back jersey
        "fabric_area_sqm": 2.0,
        "thread_meters": 250,
        "trims": {"zipper_cm": 60, "labels": 2, "drawcord_m": 1.2,
                  "eyelets": 2, "cord_stoppers": 2},
        "typical_material": "cotton_polyester_fleece",
        "making_waste_pct": 20,
        "source": "INDUSTRY_BOM",
    },
    "sweater_pullover": {
        "total_weight_g": 450,
        "fabric_weight_g": 420,
        "fabric_gsm": 250,
        "fabric_area_sqm": 1.8,
        "thread_meters": 150,
        "trims": {"labels": 2},
        "typical_material": "cotton_or_wool_knit",
        "making_waste_pct": 20,
        "source": "ECOBALYSE",
    },
    "jacket_coat": {
        "total_weight_g": 1200,
        "fabric_weight_g": 1000,
        "fabric_gsm": 450,       # from Ecobalyse
        "fabric_area_sqm": 2.5,
        "thread_meters": 600,     # Coats Group: 400-800m
        "trims": {"buttons": 5, "zipper_cm": 70, "labels": 3,
                  "lining_sqm": 2.0, "interlining_sqm": 0.5},
        "typical_material": "wool_blend_or_polyester",
        "making_waste_pct": 20,
        "source": "ECOBALYSE_COATS",
    },
    "dress": {
        "total_weight_g": 350,
        "fabric_weight_g": 300,
        "fabric_gsm": 200,
        "fabric_area_sqm": 2.0,
        "thread_meters": 180,
        "trims": {"zipper_cm": 50, "labels": 2, "buttons": 1},
        "typical_material": "viscose_or_cotton",
        "making_waste_pct": 20,
        "source": "ECOBALYSE_INDUSTRY",
    },
    "trousers_chinos": {
        "total_weight_g": 500,
        "fabric_weight_g": 450,
        "fabric_gsm": 250,
        "fabric_area_sqm": 1.6,
        "thread_meters": 200,
        "trims": {"buttons": 1, "zipper_cm": 18, "labels": 3, "hooks": 1},
        "typical_material": "cotton_twill",
        "making_waste_pct": 20,
        "source": "ECOBALYSE_INDUSTRY",
    },
    "underwear_boxers": {
        "total_weight_g": 80,
        "fabric_weight_g": 70,
        "fabric_gsm": 180,
        "fabric_area_sqm": 0.4,
        "thread_meters": 60,
        "trims": {"elastic_m": 0.8, "labels": 1},
        "typical_material": "cotton_jersey",
        "making_waste_pct": 15,
        "source": "ECOBALYSE_INDUSTRY",
    },
    "socks_pair": {
        "total_weight_g": 60,
        "fabric_weight_g": 60,
        "fabric_gsm": 250,       # knitted tube
        "thread_meters": 0,       # fully knitted
        "trims": {},
        "typical_material": "cotton_nylon_elastane_blend",
        "making_waste_pct": 2,    # fully-fashioned knit, minimal waste
        "source": "ECOBALYSE",
    },
}

# Ecobalyse product specifications (official French government data)
# surfaceMass = GSM, pcrWaste = post-cutting room waste fraction
ECOBALYSE_PRODUCTS = {
    "chemise":        {"name": "Shirt",           "gsm": 200, "fabric": "weaving",
                       "complexity": "low",   "waste": 0.20, "buttons": 11},
    "jean":           {"name": "Jeans",           "gsm": 250, "fabric": "weaving",
                       "complexity": "medium", "waste": 0.22, "zipper": 1, "rivet_button": 1},
    "jupe":           {"name": "Skirt/Dress",     "gsm": 200, "fabric": "weaving",
                       "complexity": "low",   "waste": 0.20, "zipper": 1, "buttons": 1},
    "manteau":        {"name": "Coat/Jacket",     "gsm": 450, "fabric": "weaving",
                       "complexity": "high",  "waste": 0.20, "buttons": 5, "zipper": 1},
    "pantalon":       {"name": "Pants/Shorts",    "gsm": 250, "fabric": "weaving",
                       "complexity": "medium", "waste": 0.20, "zipper": 1, "rivet_button": 1},
    "pull":           {"name": "Sweater",         "gsm": 250, "fabric": "knitting-mix",
                       "complexity": "low",   "waste": 0.20, "buttons": 5},
    "tshirt":         {"name": "T-shirt/Polo",    "gsm": 200, "fabric": "knitting-mix",
                       "complexity": "low",   "waste": 0.15, "labels": 3},
    "chaussettes":    {"name": "Socks",           "gsm": 250, "fabric": "knitting-fully-fashioned",
                       "complexity": "very-low", "waste": 0.02},
    "calecon":        {"name": "Boxers (woven)",  "gsm": 180, "fabric": "weaving",
                       "complexity": "low",   "waste": 0.15, "buttons": 2},
    "slip":           {"name": "Briefs (knit)",   "gsm": 180, "fabric": "knitting-mix",
                       "complexity": "low",   "waste": 0.15},
    "maillot_de_bain": {"name": "Swimwear",      "gsm": 220, "fabric": "knitting-mix",
                        "complexity": "low",  "waste": 0.15, "buttons": 1},
}


# =============================================================================
# 6. ECOBALYSE PROCESS DATA (French Government - open data)
# =============================================================================

# Environmental Cost Score (ECS) per kg for material production
# Higher = worse environmental impact. Unit: micro-points per kg
ECOBALYSE_MATERIAL_ECS = {
    "wool_default":         2849.0,
    "cotton":               1672.6,
    "elastane":             1042.6,
    "jute":                  884.15,
    "nylon_66":              557.77,
    "acrylic":               495.09,
    "organic_cotton":        415.0,
    "viscose":               348.98,
    "wool_new_supply_chain": 300.53,
    "hemp":                  294.42,
    "polyester_virgin":      276.22,
    "linen":                 223.81,
    "polypropylene":         192.73,
    "recycled_cotton_post_consumer": 179.46,
    "recycled_cotton_production_waste": 147.07,
    "recycled_polyester":    119.37,
    "unit": "ECS micro-points per kg",
    "source": "ECOBALYSE_GITHUB",
}

# Ecobalyse transformation process energy requirements
# elecMJ = electricity in MJ/kg, heatMJ = thermal energy in MJ/kg
ECOBALYSE_TRANSFORMATION_ENERGY = {
    "spinning_conventional_40nm": {"elecMJ": 13.104, "heatMJ": 0,    "waste": 0.12},
    "spinning_unconventional_40nm": {"elecMJ": 6.552, "heatMJ": 0,   "waste": 0.12},
    "spinning_filament_40nm":     {"elecMJ": 4.896,  "heatMJ": 0,    "waste": 0.03},
    "weaving_40nm_250gsm":        {"elecMJ": 20.952, "heatMJ": 0,    "waste": 0.0625},
    "circular_knitting":          {"elecMJ": 4.251,  "heatMJ": 0,    "waste": 0.034},
    "fully_fashioned_knitting":   {"elecMJ": 6.064,  "heatMJ": 0,    "waste": 0.005},
    "seamless_knitting":          {"elecMJ": 13.211, "heatMJ": 0,    "waste": 0.005},
    "batch_dyeing":               {"elecMJ": 4.32,   "heatMJ": 32.4, "waste": 0},
    "continuous_dyeing":          {"elecMJ": 2.88,   "heatMJ": 16.2, "waste": 0},
    "average_dyeing":             {"elecMJ": 3.6,    "heatMJ": 24.3, "waste": 0},
    "bleaching":                  {"elecMJ": 0.72,   "heatMJ": 5.4,  "waste": 0},
    "desizing":                   {"elecMJ": 0.36,   "heatMJ": 3.2,  "waste": 0},
    "mercerizing":                {"elecMJ": 0.36,   "heatMJ": 2.7,  "waste": 0},
    "scouring_wool":              {"elecMJ": 1.08,   "heatMJ": 13.5, "waste": 0},
    "chemical_finishing":         {"elecMJ": 2.16,   "heatMJ": 13.5, "waste": 0},
    "washing_synthetics":         {"elecMJ": 0.72,   "heatMJ": 10.8, "waste": 0},
    "chemical_fading":            {"elecMJ": 6.53,   "heatMJ": 37.81, "waste": 0},
    "unit": "MJ per kg of textile processed",
    "source": "ECOBALYSE_GITHUB",
}

# Ecobalyse dyeing ECS by fiber chemistry
ECOBALYSE_DYEING_ECS = {
    "cellulosic_fibers": {"ecs": 1626.9, "note": "cotton, viscose, linen"},
    "synthetic_fibers":  {"ecs": 620.3,  "note": "polyester, nylon, acrylic"},
    "pigment_printing":  {"ecs": 2026.2},
    "reactive_printing": {"ecs": 787.71},
    "bleaching":         {"ecs": 757.66},
    "source": "ECOBALYSE_GITHUB",
}


# =============================================================================
# 7. FUEL CONVERSION FACTORS (for calculating CO2 from energy)
# =============================================================================

# Source: PMC/Heliyon study - IPCC-based factors
FUEL_EMISSION_FACTORS = {
    # kg CO2 per MJ
    "natural_gas":   {"co2_kg_per_mj": 0.0561},
    "coal":          {"co2_kg_per_mj": 0.0946},
    "diesel":        {"co2_kg_per_mj": 0.0741},
    "heavy_fuel_oil": {"co2_kg_per_mj": 0.0774},
    "furnace_oil":   {"co2_kg_per_mj": 0.0774},
    "biomass":       {"co2_kg_per_mj": 0.1000},
    "wood":          {"co2_kg_per_mj": 0.1120},
    "source": "PMC_HELIYON",
}

# Grid electricity emission factors for major textile-producing countries
# (useful for converting Ecobalyse elecMJ to CO2)
ELECTRICITY_GRID_FACTORS = {
    # kg CO2e per kWh (1 kWh = 3.6 MJ)
    "china":       {"kg_co2e_per_kwh": 0.555},
    "india":       {"kg_co2e_per_kwh": 0.708},
    "bangladesh":  {"kg_co2e_per_kwh": 0.528},
    "vietnam":     {"kg_co2e_per_kwh": 0.476},
    "turkey":      {"kg_co2e_per_kwh": 0.418},
    "indonesia":   {"kg_co2e_per_kwh": 0.692},
    "france":      {"kg_co2e_per_kwh": 0.052},
    "eu_average":  {"kg_co2e_per_kwh": 0.233},
    "usa":         {"kg_co2e_per_kwh": 0.379},
    "source": "IEA_2023",
    "note": "Multiply elecMJ/3.6 * factor to get kg CO2e from electricity"
}


# =============================================================================
# 8. FREE APIs AND DOWNLOADABLE DATASETS
# =============================================================================

FREE_DATA_SOURCES = {
    "ecobalyse_api": {
        "url": "https://ecobalyse.beta.gouv.fr/",
        "api_docs": "https://ecobalyse.beta.gouv.fr/#/api",
        "github": "https://github.com/MTES-MCT/ecobalyse",
        "data_repo": "https://github.com/MTES-MCT/ecobalyse-data",
        "type": "REST API (requires free token)",
        "description": "French government official textile LCA tool. Calculates full PEF "
                       "across 16 environmental indicators. Based on Ecoinvent + Agribalyse. "
                       "Raw JSON data freely available on GitHub.",
        "endpoints": {
            "GET /textile/countries": "List of countries for simulations",
            "GET /textile/materials": "List of 16 fabric materials (cotton, polyester, wool, etc.)",
            "GET /textile/products": "List of 11 garment types with default specs",
            "GET /textile/trims": "List of trims (buttons, zippers, etc.)",
            "POST /textile/simulator": "Calculate environmental impacts for a garment",
            "POST /textile/simulator/detailed": "Detailed impact with stage breakdown",
        },
        "data_files": {
            "materials": "https://raw.githubusercontent.com/MTES-MCT/ecobalyse/master/public/data/textile/materials.json",
            "products": "https://raw.githubusercontent.com/MTES-MCT/ecobalyse/master/public/data/textile/products.json",
            "processes": "https://raw.githubusercontent.com/MTES-MCT/ecobalyse/master/public/data/processes.json",
        },
        "coverage": "16 materials, 11 garment types, full lifecycle stages",
        "license": "Open source (French government)",
    },
    "carbonfact_database": {
        "url": "https://www.carbonfact.com/carbon-footprint",
        "type": "Web reference (no API, but data is publicly listed)",
        "description": "Comprehensive per-garment CO2e values for 50+ garment types. "
                       "PEF-aligned methodology.",
        "coverage": "50+ garment categories, total lifecycle CO2e",
    },
    "climatiq_api": {
        "url": "https://www.climatiq.io/",
        "api_docs": "https://www.climatiq.io/data",
        "type": "REST API (free tier available)",
        "description": "55 textile emission factors from EXIOBASE, UK Gov data, etc. "
                       "Both weight-based (kg/tonne) and spend-based (kg/GBP, kg/EUR).",
        "coverage": "Textiles, clothing, footwear categories",
    },
    "openco2net": {
        "url": "https://www.openco2.net/en/",
        "type": "API + web tool",
        "description": "European emission factor database with API. Includes textile categories.",
    },
    "higg_msi": {
        "url": "https://cascale.org/tools-programs/higg-index-tools/product-tools/",
        "registration": "https://higg.org",
        "type": "Web tool (free registration for SMEs)",
        "description": "SAC/Cascale Material Sustainability Index. Free for designers at SMEs. "
                       "Backed by Sphera LCA database. Covers global warming, water scarcity, "
                       "eutrophication, fossil fuel, chemistry.",
        "note": "Raw data not downloadable; must use through web interface",
    },
    "openlca_nexus": {
        "url": "https://nexus.openlca.org/databases",
        "type": "Downloadable LCA databases",
        "description": "300,000+ LCA datasets. Free databases include Agribalyse (food/agriculture), "
                       "ELCD, and others. Ecoinvent (most comprehensive for textiles) requires license. "
                       "openLCA software itself is free and open source.",
        "free_textile_data": "Limited - mostly in paid Ecoinvent database",
    },
    "wrap_reports": {
        "url": "https://www.truevaluemetrics.org/DBpdfs/Issues/SupplyChain/Textiles/WRAP-REPORT-10.7.12%20VOC-%20FINAL.pdf",
        "type": "PDF report with data tables",
        "description": "WRAP 'Valuing Our Clothes' - foundational UK data on clothing carbon footprints. "
                       "Emission factors per kg of fabric by fiber type.",
    },
    "github_abeer_textile_lca": {
        "url": "https://github.com/Abeer-Wal/Textile-LCA-Data-Visualization",
        "type": "GitHub repo with visualization code",
        "description": "Python project for visualizing textile LCA data including carbon emissions, "
                       "water use, and energy consumption across production stages.",
    },
}


# =============================================================================
# 9. SOURCE REFERENCES
# =============================================================================

SOURCES = {
    "WRAP_2012": {
        "title": "Valuing Our Clothes: the evidence base",
        "author": "WRAP (Waste & Resources Action Programme)",
        "year": 2012,
        "url": "https://www.ethicalconsumer.org/fashion-clothing/carbon-cost-clothing",
        "pdf": "https://www.truevaluemetrics.org/DBpdfs/Issues/SupplyChain/Textiles/WRAP-REPORT-10.7.12%20VOC-%20FINAL.pdf",
    },
    "WRAP_UK_CLOTHING": {
        "title": "A Carbon Footprint for UK Clothing and Opportunities for Savings",
        "author": "Bernie Thomas, Matt Fishwick, James Joyce, Anton van Santen (WRAP)",
        "url": "https://www.co2everything.com/co2e-of/polyester",
        "note": "Table 21 - per 2 sq meters at 150gsm",
    },
    "PMC_HELIYON": {
        "title": "Assessing the potential of GHG emissions for the textile sector: A baseline study",
        "author": "Various (Pakistan textile sector study)",
        "year": 2023,
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10700620/",
        "doi": "Published in Heliyon",
    },
    "OECOTEXTILES": {
        "title": "Estimating the carbon footprint of a fabric",
        "author": "OEcotextiles",
        "year": 2011,
        "url": "https://oecotextiles.blog/2011/01/19/estimating-the-carbon-footprint-of-a-fabric/",
    },
    "8BILLIONTREES": {
        "title": "Carbon Footprint of Polyester vs Cotton vs Wool vs Leather vs Nylon",
        "url": "https://8billiontrees.com/carbon-offsets-credits/carbon-footprint-of-polyester/",
    },
    "HEMPFOUNDATION": {
        "title": "7 Major Fibers & Textiles In The World And Their Carbon Footprint",
        "url": "https://hempfoundation.net/7-major-fibers-textiles-in-the-world-and-their-carbon-footprint/",
    },
    "CARBONFACT": {
        "title": "Carbon Footprint of Fashion Products",
        "url": "https://www.carbonfact.com/carbon-footprint",
        "note": "PEF-aligned methodology, comprehensive garment database",
    },
    "CARBON_TRUST": {
        "title": "Carbon Trust clothing carbon footprint estimates",
        "url": "https://www.ethicalconsumer.org/fashion-clothing/carbon-cost-clothing",
    },
    "PLANBE": {
        "title": "Fashion Carbon Footprint: How to Measure Emissions in the Apparel Industry",
        "url": "https://planbe.eco/en/blog/carbon-footprint-and-water-footprint-calculating-in-the-fashion-industry/",
    },
    "FUTURE_GREEN": {
        "title": "Carbon Footprint and Price Comparison: Secondhand vs. New Clothing",
        "url": "https://www.futurecard.co/futureblog/carbon-footprint-and-price-comparison-secondhand-vs-new-clothing",
    },
    "WATER_FOOTPRINT_NETWORK": {
        "title": "Water footprint assessment of polyester and viscose",
        "url": "https://waterfootprint.org/resources/WFA_Polyester_and__Viscose_2017.pdf",
    },
    "ECOBALYSE_GITHUB": {
        "title": "Ecobalyse - French Government Environmental Labeling Tool",
        "url": "https://github.com/MTES-MCT/ecobalyse",
        "data": "https://github.com/MTES-MCT/ecobalyse-data",
        "api": "https://ecobalyse.beta.gouv.fr/#/api",
    },
    "IEA_2023": {
        "title": "IEA Emission Factors (approximate values)",
        "note": "Grid emission factors vary by year; these are approximate 2022-2023 values",
    },
    "ILO": {
        "title": "Carbon emissions in the textile and garment sector",
        "url": "https://www.ilo.org/media/375386/download",
    },
    "EU_PEF": {
        "title": "PEFCR for Apparel and Footwear",
        "url": "https://pefapparelandfootwear.eu/",
        "note": "EU Product Environmental Footprint Category Rules - approved 2025",
    },
    "ACADEMIC_LCA": {
        "note": "Various peer-reviewed LCA studies on textile dyeing and finishing",
    },
    "INDUSTRY_BOM": {
        "note": "Compiled from multiple garment manufacturing references including "
                "onlineclothingstudy.com, worldfashionexchange.com, Coats Group data",
    },
    "ECOBALYSE_COATS": {
        "note": "Ecobalyse product specs + Coats Group thread consumption data",
    },
    "FULGAR": {
        "title": "Water consumption in the textile industry",
        "url": "https://www.fulgar.com/en/feature/282/water-consumption-in-the-textile-industry",
    },
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def estimate_garment_co2(garment_type: str, fiber: str = "cotton") -> dict:
    """
    Quick estimate of kg CO2e for a garment, combining fiber + garment data.

    This is a simplified calculation. For production-grade estimates,
    use the Ecobalyse API.
    """
    bom = GARMENT_BOM.get(garment_type)
    fiber_data = CO2_PER_KG_FIBER.get(fiber)

    if not bom or not fiber_data:
        available_garments = list(GARMENT_BOM.keys())
        available_fibers = list(CO2_PER_KG_FIBER.keys())
        return {"error": f"Unknown garment or fiber. "
                f"Garments: {available_garments}, Fibers: {available_fibers}"}

    fabric_kg = bom["fabric_weight_g"] / 1000
    waste_multiplier = 1 + bom["making_waste_pct"] / 100
    total_fiber_kg = fabric_kg * waste_multiplier

    co2_fiber = total_fiber_kg * fiber_data["kg_co2e_per_kg"]

    return {
        "garment": garment_type,
        "fiber": fiber,
        "fabric_kg": fabric_kg,
        "total_fiber_with_waste_kg": round(total_fiber_kg, 3),
        "estimated_co2e_kg": round(co2_fiber, 2),
        "note": "This covers raw material + fabric production only. "
                "Add transport, use-phase (washing), and end-of-life for full lifecycle.",
        "for_comparison": CO2_PER_GARMENT_CARBONFACT.get(garment_type, {}).get("kg_co2e", "N/A"),
    }


if __name__ == "__main__":
    print("=== Garment Environmental Impact Data ===\n")

    print("Sample fiber CO2 emissions (kg CO2e/kg):")
    for fiber, data in CO2_PER_KG_FIBER.items():
        print(f"  {fiber:15s}: {data['kg_co2e_per_kg']:5.1f} kg CO2e/kg")

    print("\nSample garment CO2 (Carbonfact, total lifecycle):")
    for garment in ["t_shirt", "jeans", "hoodie", "jacket", "dress"]:
        data = CO2_PER_GARMENT_CARBONFACT.get(garment, {})
        print(f"  {garment:15s}: {data.get('kg_co2e', 'N/A'):5.2f} kg CO2e")

    print("\nSample estimates:")
    for g, f in [("t_shirt", "cotton"), ("jeans", "cotton"),
                 ("hoodie", "polyester"), ("jacket_coat", "wool")]:
        result = estimate_garment_co2(g, f)
        if "error" not in result:
            print(f"  {g} ({f}): ~{result['estimated_co2e_kg']} kg CO2e "
                  f"(Carbonfact reference: {result['for_comparison']})")

    print(f"\nFree APIs: {len(FREE_DATA_SOURCES)} sources documented")
    for name, info in FREE_DATA_SOURCES.items():
        print(f"  {name}: {info.get('url', 'N/A')}")
