from aiogram.types import Message
from db import db

async def show_slots(msg: Message):
    slots = await db.pool.fetch("""
        SELECT date, time FROM schedule WHERE available=TRUE 
        ORDER BY date, time LIMIT 20
    """)
    if not slots:
        await msg.answer("Свободного времени пока нет")
        return
    text = "Свободное время:\n\n"
    for s in slots:
        text += f"{s['date'].strftime('%d.%m (%a)')} — {str(s['time'])[:-3]}\n"
    await msg.answer(text)

async def show_price(msg: Message):
    prices = await db.pool.fetch("SELECT service_name, price FROM price_list")
    text = "Прайс-лист:\n\n" + "\n".join([f"• {p['service_name']} — {p['price']}₽" for p in prices])
    await msg.answer(text)