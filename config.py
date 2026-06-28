from dotenv import load_dotenv
import os

load_dotenv()

def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Переменная окружения {name} не задана. Заполните .env файл.")
    return value

ROUTER_AI_API_KEY = _require("ROUTER_AI_API_KEY")
TODOIST_API_KEY = _require("TODOIST_API_KEY")
TELEGRAM_BOT_TOKEN = _require("TELEGRAM_BOT_TOKEN")
PROXY_URL = os.getenv("PROXY_URL") or None
