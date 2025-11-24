import ollama
import json
import re
from datetime import datetime
from config import OLLAMA_MODEL

async def parse_intent(text: str) -> dict:
    prompt = f"""Ты — Аня, ассистент салона красоты.
Анализируй сообщение и извлекай информацию. Отвечай ТОЛЬКО валидным JSON!

Формат ответа:
{{
  "action": "show_slots" | "show_price" | "book" | "cancel" | "unknown",
  "date": "2025-11-27" или null,
  "time": "15:00" или null,
  "service": "маникюр" или "педикюр" или "наращивание" или "брови" или null,
  "appointment_id": число или null
}}

Правила:
- "show_slots": запрос свободного времени ("свободное время", "когда свободно", "расписание", "доступное время")
- "show_price": запрос цен ("прайс", "сколько стоит", "цены", "услуги", "что делаете")
- "book": запрос на запись ("записаться", "хочу запись", "запиши", "запись", "могу записать")
- "cancel": отмена записи ("отменить", "отмена записи", "отменить запись")
- Для даты используй формат ГГГГ-ММ-ДД
- Для времени используй формат ЧЧ:ММ
- appointment_id извлекай из текста (например "отменить 5" -> 5)

Сообщение: "{text}"
JSON:"""

    try:
        resp = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            options={"temperature": 0.1, "num_predict": 200}
        )
        raw = resp['response']
        print("🤖 ИИ ответил:", raw)

        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            return {"action": "unknown"}

        data = json.loads(raw[start:end])

        if data.get("date"):
            data["date"] = await normalize_date(data["date"])

        return data
        
    except Exception as e:
        print("❌ Ошибка ИИ:", e)
        return {"action": "unknown"}

async def normalize_date(date_str: str) -> str:
    """Нормализует дату в формат YYYY-MM-DD"""
    try:
        formats = [
            "%Y-%m-%d", "%d.%m.%Y", "%d.%m", "%d/%m/%Y", 
            "%d/%m", "%d-%m-%Y", "%d-%m"
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                if fmt in ["%d.%m", "%d/%m", "%d-%m"]:
                    current_year = datetime.now().year
                    if parsed.replace(year=current_year) < datetime.now():
                        parsed = parsed.replace(year=current_year + 1)
                    else:
                        parsed = parsed.replace(year=current_year)
                return parsed.strftime("%Y-%m-%d")
            except:
                continue
                
        return date_str
    except:
        return date_str