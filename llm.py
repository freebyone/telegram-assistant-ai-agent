import ollama
import json
from dotenv import load_dotenv
import os

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "gemma2:9b")

async def get_intent(text: str) -> str:
    prompt = f"""
Ты — ассистент салона красоты. Определи намерение пользователя и ответь ТОЛЬКО одним словом:

book — хочет записаться
price — спрашивает цены
schedule — спрашивает когда свободно
cancel — хочет отменить
unknown — всё остальное

Сообщение: "{text}"
Ответ:
"""
    try:
        resp = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
        answer = resp["message"]["content"].strip().lower()
        if answer in ["book", "price", "schedule", "cancel"]:
            return answer
        return "unknown"
    except:
        return "unknown"