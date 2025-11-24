from aiogram.types import Message
from db import db

async def show_slots(msg: Message):
    try:
        slots = await db.pool.fetch("""
            SELECT date, time FROM schedule 
            WHERE available = TRUE 
            AND date >= CURRENT_DATE
            ORDER BY date, time 
            LIMIT 30
        """)
        
        if not slots:
            await msg.answer("📭 <b>Свободного времени пока нет</b>\n\nПопробуйте позже!")
            return
        
        text = "🕒 <b>Свободное время:</b>\n\n"
        current_date = None
        
        for s in slots:
            slot_date = s['date']
            slot_time = str(s['time'])[:5]
            
            if current_date != slot_date:
                if current_date is not None:
                    text += "\n"
                current_date = slot_date
                text += f"📅 <b>{slot_date.strftime('%d.%m.%Y (%A)')}</b>\n"
            
            text += f"   ⏰ {slot_time}\n"
        
        await msg.answer(text)
        
    except Exception as e:
        await msg.answer("❌ <b>Ошибка при получении расписания</b>\n\nПопробуйте позже.")
        print(f"Ошибка в show_slots: {e}")

async def show_price(msg: Message):
    try:
        prices = await db.pool.fetch("SELECT service_name, price, duration FROM price_list ORDER BY id")
        
        text = "💰 <b>Прайс-лист:</b>\n\n"
        for p in prices:
            text += f"• {p['service_name']} — <b>{p['price']}₽</b>"
            if p['duration']:
                text += f" ({p['duration']} мин)"
            text += "\n"
        
        text += "\n💬 <i>Чтобы записаться, просто напишите желаемую дату и время!</i>"
        await msg.answer(text)
        
    except Exception as e:
        await msg.answer("❌ <b>Ошибка при получении прайс-листа</b>")
        print(f"Ошибка в show_price: {e}")