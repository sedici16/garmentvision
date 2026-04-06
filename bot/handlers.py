"""Telegram message handlers with two-step flow (garment + optional labels)."""

from __future__ import annotations

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from bot.config import DASHBOARD_BASE_URL
from bot.vision import classify_image, identify_garment, read_label
from bot.calculator import calculate_impact
from bot.ecobalyse import query_ecobalyse
from bot.greta import greta_judge
from bot.db import log_scan

logger = logging.getLogger(__name__)

WELCOME_MSG = (
    "Welcome to <b>GarmentScan</b>! 👕🌍\n\n"
    "Send me a photo of any clothing item and I'll calculate:\n"
    "1. <b>Bill of Materials</b> — fabric, trims, components\n"
    "2. <b>CO2 Emissions</b> — full lifecycle carbon footprint\n"
    "3. <b>Water Usage</b> — from fiber to finished garment\n"
    "4. <b>Production Data</b> — sewing time, cost, machines\n\n"
    "You can send:\n"
    "📸 A <b>garment photo</b> — I'll identify and estimate materials\n"
    "🏷️ A <b>label photo</b> — I'll read exact composition\n"
    "📸+🏷️ <b>Both</b> — best accuracy!\n\n"
    "Just snap a photo and send it!"
)

# Per-chat conversation state
# {chat_id: {"garment": {...}, "labels": [{...}], "stage": "waiting_label"|"done"}}
_sessions: dict[int, dict] = {}


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MSG, parse_mode=ParseMode.HTML)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MSG, parse_mode=ParseMode.HTML)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(ChatAction.TYPING)
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    await _process_image(update, context, bytes(image_bytes), "image/jpeg")


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        return
    await update.message.chat.send_action(ChatAction.TYPING)
    file = await doc.get_file()
    image_bytes = await file.download_as_bytearray()
    await _process_image(update, context, bytes(image_bytes), doc.mime_type or "image/jpeg")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "skip_label":
        session = _sessions.get(chat_id)
        if session and session.get("garment"):
            await query.message.edit_text("📊 Calculating with estimated materials...")
            await _generate_report(query.message, chat_id, update.effective_user)
        else:
            await query.message.edit_text("No garment data found. Send a new photo.")

    elif query.data == "done_labels":
        session = _sessions.get(chat_id)
        if session and session.get("garment"):
            await query.message.edit_text("📊 Calculating with exact label data...")
            await _generate_report(query.message, chat_id, update.effective_user)
        else:
            await query.message.edit_text("No garment data found. Send a new photo.")


async def _process_image(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes, media_type: str):
    """Classify image and route to garment or label flow."""
    chat_id = update.message.chat_id
    status_msg = await update.message.reply_text("🔍 Analyzing image...")

    # Classify what the image is
    classification = classify_image(image_bytes, media_type)
    if not classification:
        await status_msg.edit_text("❌ Couldn't analyze this image. Try again.")
        return

    image_type = classification.get("image_type", "other")
    logger.info("Image classified as: %s", image_type)

    if image_type == "label":
        await _handle_label_image(update, status_msg, image_bytes, media_type, chat_id)
    elif image_type == "garment":
        await _handle_garment_image(update, status_msg, image_bytes, media_type, chat_id)
    else:
        await status_msg.edit_text(
            "❌ This doesn't look like clothing or a label.\n"
            "Please send a photo of a garment or its care/composition label."
        )


async def _handle_garment_image(update: Update, status_msg, image_bytes: bytes, media_type: str, chat_id: int):
    """Process garment photo — step 1."""
    await status_msg.edit_text("👕 Identifying garment...")

    garment = identify_garment(image_bytes, media_type)
    if not garment or garment.get("confidence") == "none":
        await status_msg.edit_text("❌ Couldn't identify a garment. Please try a clearer photo.")
        return

    # Store in session
    _sessions[chat_id] = {
        "garment": garment,
        "labels": [],
        "stage": "waiting_label",
    }

    garment_type = garment.get("garment_type", "Unknown")
    materials_str = ", ".join(
        f"{m['percentage']}% {m['fiber']}" for m in garment.get("materials", [])
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏷️ Add label photo", callback_data="noop")],
        [InlineKeyboardButton("⏭️ Skip — use estimates", callback_data="skip_label")],
    ])

    await status_msg.edit_text(
        f"👕 <b>{garment_type}</b>\n"
        f"🧵 Estimated: {materials_str}\n"
        f"⚖️ ~{garment.get('estimated_weight_grams', '?')}g\n\n"
        f"🏷️ <b>Want to add a label photo for exact materials?</b>\n"
        f"Send up to 2 label photos, or tap Skip.",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


async def _handle_label_image(update: Update, status_msg, image_bytes: bytes, media_type: str, chat_id: int):
    """Process label photo."""
    await status_msg.edit_text("🏷️ Reading label...")

    label = read_label(image_bytes, media_type)
    if not label or label.get("confidence") == "none":
        await status_msg.edit_text("❌ Couldn't read this label. Try a clearer, well-lit photo.")
        return

    session = _sessions.get(chat_id)

    if session and session.get("garment") and session["stage"] == "waiting_label":
        # Adding label to existing garment session
        session["labels"].append(label)
        label_count = len(session["labels"])

        materials_str = ", ".join(
            f"{m['percentage']}% {m['fiber']}" for m in label.get("materials", [])
        )
        country = label.get("country_of_origin", "")
        country_str = f"\n🌍 Made in: {country}" if country else ""

        if label_count >= 2:
            # Max labels reached, generate report
            await status_msg.edit_text(
                f"🏷️ Label {label_count} read: {materials_str}{country_str}\n"
                f"📊 Calculating with exact data...",
                parse_mode=ParseMode.HTML,
            )
            await _generate_report(status_msg, chat_id, update.effective_user)
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏷️ Add another label", callback_data="noop")],
                [InlineKeyboardButton("✅ Done — calculate!", callback_data="done_labels")],
            ])
            await status_msg.edit_text(
                f"🏷️ Label read: <b>{materials_str}</b>{country_str}\n\n"
                f"Send another label photo or tap Done.",
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
    else:
        # Label first — no garment yet
        _sessions[chat_id] = {
            "garment": None,
            "labels": [label],
            "stage": "waiting_garment",
        }

        materials_str = ", ".join(
            f"{m['percentage']}% {m['fiber']}" for m in label.get("materials", [])
        )
        country = label.get("country_of_origin", "")
        country_str = f"\n🌍 Made in: {country}" if country else ""

        await status_msg.edit_text(
            f"🏷️ Label read: <b>{materials_str}</b>{country_str}\n\n"
            f"📸 Now send a photo of the <b>garment itself</b> so I can identify the type and construction.",
            parse_mode=ParseMode.HTML,
        )


async def _generate_report(message, chat_id: int, user):
    """Merge garment + label data and generate the impact report."""
    session = _sessions.get(chat_id)
    if not session or not session.get("garment"):
        await message.reply_text("No garment data. Send a garment photo first.")
        return

    garment = session["garment"]
    labels = session.get("labels", [])

    # Merge label data into garment
    if labels:
        # Use first label's materials (most reliable)
        label = labels[0]
        if label.get("materials"):
            garment["materials"] = label["materials"]
            garment["materials_source"] = "label"

        # Country of origin from any label
        for l in labels:
            if l.get("country_of_origin"):
                garment["country_of_origin"] = l["country_of_origin"]
                break

        # Care instructions
        for l in labels:
            if l.get("care_instructions"):
                garment["care_instructions"] = l["care_instructions"]
                break

        # Brand
        for l in labels:
            if l.get("brand"):
                garment["brand"] = l["brand"]
                break

    # Calculate impact
    impact = calculate_impact(garment)

    # Try Ecobalyse
    ecobalyse = query_ecobalyse(garment)

    # Greta Mode
    greta = greta_judge(garment, impact)

    # Log
    primary_material = garment.get("materials", [{}])[0].get("fiber", "unknown")
    if user:
        log_scan(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            garment_type=garment.get("garment_type", "unknown"),
            garment_category=garment.get("garment_category", "unknown"),
            primary_material=primary_material,
            co2_kg=impact["co2"]["total_kg_co2e"],
            water_liters=impact["water"]["total_liters"],
        )

    # Clear session
    _sessions.pop(chat_id, None)

    # Send report
    await _send_report(message, garment, impact, ecobalyse, greta)


async def _send_report(message, garment: dict, impact: dict, ecobalyse: dict = None, greta: dict = None):
    """Format and send the environmental impact report."""
    co2 = impact["co2"]
    water = impact["water"]
    bom = impact["bom"]
    prod = impact["production"]

    materials_str = ", ".join(
        f"{m['percentage']}% {m['fiber']}" for m in garment.get("materials", [])
    )
    source_tag = " (from label)" if garment.get("materials_source") == "label" else " (estimated)"

    lines = [
        f"👕 <b>{garment.get('garment_type', 'Unknown')}</b>",
        f"🧵 {materials_str}{source_tag}",
        f"⚖️ ~{garment.get('estimated_weight_grams', '?')}g · {garment.get('fabric_type', '?')} · {garment.get('fabric_weight_gsm', '?')} GSM",
        f"🎨 {garment.get('color', '?')} · {garment.get('finish', 'standard')}",
    ]

    if garment.get("country_of_origin"):
        lines.append(f"🌍 Made in: {garment['country_of_origin']}")
    if garment.get("brand"):
        lines.append(f"🏷️ Brand: {garment['brand']}")

    # CO2
    lines.append("")
    lines.append(f"🌍 <b>CO2 Footprint: {co2['total_kg_co2e']} kg CO2e</b>")
    for stage, val in co2["stage_breakdown"].items():
        stage_label = stage.replace("_", " ").title()
        lines.append(f"   {stage_label}: {val} kg")
    lines.append(f"   Transport: {co2['transport_co2']} kg")
    lines.append(f"   = {co2['equivalent_km_driven']} km driven")
    lines.append(f"   = {co2['equivalent_phone_charges']} phone charges")

    # Water
    lines.append("")
    lines.append(f"💧 <b>Water: {water['total_liters']:,} liters</b>")
    for fb in water["fiber_breakdown"]:
        lines.append(f"   {fb['fiber'].title()}: {fb['liters_total']:,} L")
    lines.append(f"   Dyeing: {water['dyeing_liters']:,} L")
    lines.append(f"   = {water['equivalent_showers']} showers")

    # BOM
    lines.append("")
    lines.append("📋 <b>Bill of Materials:</b>")
    for item in bom["items"][:8]:
        lines.append(f"   {item['component']}: {item['quantity']} ({item['weight_g']}g)")
    lines.append(f"   Cutting waste: ~{bom['cutting_waste_pct']}%")
    lines.append(f"   Fabric area: {bom['fabric_area_sqm']} m²")

    # Production
    lines.append("")
    lines.append("🏭 <b>Production:</b>")
    lines.append(f"   Total time: {prod['total_time_minutes']} min")
    for stage, mins in prod["time_breakdown_minutes"].items():
        lines.append(f"   {stage.replace('_', ' ').title()}: {mins} min")
    lines.append(f"   CMT cost: ${prod['cmt_cost_usd']:.2f}")
    lines.append(f"   Machines: {', '.join(prod['machines_required'][:3])}")
    lines.append(f"   Typical origin: {prod['typical_production_country']}")
    lines.append(f"   Min order: {prod['minimum_order_qty']} pcs")

    # Care instructions from label
    if garment.get("care_instructions"):
        lines.append("")
        lines.append("🧼 <b>Care:</b>")
        for instr in garment["care_instructions"][:4]:
            lines.append(f"   {instr}")

    # Ecobalyse
    if ecobalyse and ecobalyse.get("climate_change_kg"):
        lines.append("")
        lines.append("🇫🇷 <b>Ecobalyse (EU PEF):</b>")
        lines.append(f"   Climate: {ecobalyse['climate_change_kg']:.2f} kg CO2e")
        if ecobalyse.get("pef_score"):
            lines.append(f"   PEF score: {ecobalyse['pef_score']:.0f} µPt")

    # Greta Mode
    if greta:
        color_emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("🌱 <b>GRETA MODE</b>")
        lines.append("")
        c = color_emoji.get(greta["carbon"], "⚪")
        lines.append(f"{c} <b>Carbon:</b> {greta['carbon']}")
        if greta.get("carbon_comment"):
            lines.append(f"   {greta['carbon_comment']}")
        w = color_emoji.get(greta["water"], "⚪")
        lines.append(f"{w} <b>Water:</b> {greta['water']}")
        if greta.get("water_comment"):
            lines.append(f"   {greta['water_comment']}")
        o = color_emoji.get(greta["overall"], "⚪")
        lines.append(f"{o} <b>Overall:</b> {greta['overall']}")
        if greta.get("overall_comment"):
            lines.append(f"   {greta['overall_comment']}")

    text = "\n".join(lines)
    await message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
