import os
import sys
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("hf")

HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
VISION_MODEL = "Qwen/Qwen2.5-VL-72B-Instruct"
ANALYST_MODEL = "Qwen/Qwen2.5-72B-Instruct"

ECOBALYSE_API = "https://ecobalyse.beta.gouv.fr/api"

DASHBOARD_BASE_URL = os.getenv("DASHBOARD_BASE_URL", "http://83.136.105.116:5002")

_REQUIRED = {
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "hf": HF_TOKEN,
}


def validate():
    missing = [name for name, val in _REQUIRED.items() if not val]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)
