import ollama
import json
import re
from datetime import datetime

async def parse_intent(text: str) -> dict:
    prompt = f"""Ты — Аня, ассистент салона красоты.
Ответь ТОЛЬКО валидным JSON и ничем больше!

{{
  "action": "show_slots" | "show_price" | "book" | "cancel" | "unknown",
  "date": "2025-11-27" или null,
  "time": "15:00" или null,
  "service": "маникюр" или "педикюр" или null,
  "appointment_id": число или null
}}

Сообщение: "{text}"
JSON:"""

    try:
        resp = ollama.generate(
            model="gemma2:9b",
            prompt=prompt,
            options={"temperature": 0.0, "num_predict": 200}
        )
        raw = resp['response']
        print("ИИ сказал:", raw)

        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            return {"action": "unknown"}

        data = json.loads(raw[start:end])

        if data.get("date"):
            try:
                for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m", "%d/%m"):
                    try:
                        parsed = datetime.strptime(data["date"], fmt)
                        data["date"] = parsed.strftime("%Y-%m-%d")
                        break
                    except:
                        continue
            except:
                pass

        return data
    except Exception as e:
        print("Ошибка ИИ:", e)
        return {"action": "unknown"}