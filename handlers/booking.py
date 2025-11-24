from aiogram.types import Message
from db import db
from datetime import datetime, time
import logging

async def try_book(msg: Message, date_str: str, time_str: str, service: str = None):
    try:
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(time_str, "%H:%M").time()
    except Exception as e:
        logging.error(f"Ошибка парсинга даты/времени: {e}")
        await msg.answer(
            "❓ <b>Не поняла дату или время</b>\n\n"
            "Пожалуйста, укажите в формате:\n"
            "<i>\"27 ноября в 15:00\"</i>\n"
            "<i>\"На завтра в 14:30\"</i>"
        )
        return

    service_id = None
    service_name = "услуга"
    if service:
        service_mapping = {
            "маникюр": 1, "маникюр + покрытие": 1,
            "педикюр": 2, 
            "наращивание": 3,
            "брови": 4
        }
        service_id = service_mapping.get(service.lower())
        
        async with db.pool.acquire() as conn:
            if service_id:
                service_record = await conn.fetchrow(
                    "SELECT service_name FROM price_list WHERE id = $1", 
                    service_id
                )
                if service_record:
                    service_name = service_record['service_name']

    async with db.pool.acquire() as conn:
        async with conn.transaction():
            available = await conn.fetchval("""
                SELECT available FROM schedule 
                WHERE date = $1 AND time = $2
            """, appointment_date, appointment_time)

            if not available:
                await msg.answer(
                    "❌ <b>Это время уже занято</b>\n\n"
                    "Вот ближайшее свободное время:"
                )
                from .common import show_slots
                await show_slots(msg)
                return

            app_id = await conn.fetchval("""
                INSERT INTO appointments 
                (client_tg_id, client_name, service_id, appointment_date, appointment_time)
                VALUES ($1, $2, $3, $4, $5) RETURNING id
            """, msg.from_user.id, msg.from_user.full_name, service_id, appointment_date, appointment_time)

            await conn.execute("""
                UPDATE schedule 
                SET available = FALSE
                WHERE date = $1 AND time = $2
            """, appointment_date, appointment_time)

            await msg.answer(
                "✅ <b>Запись успешно создана!</b>\n\n"
                f"📅 <b>{appointment_date.strftime('%d.%m.%Y')}</b>\n"
                f"⏰ <b>{time_str}</b>\n"
                f"💅 <b>{service_name}</b>\n"
                f"🔢 <b>Номер записи: #{app_id}</b>\n\n"
                "Мы напомним вам о визите за 24 часа!\n"
                "Для отмены отправьте номер записи.",
            )

async def cancel_booking(msg: Message, appointment_id: int):
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            result = await conn.fetchrow("""
                UPDATE appointments 
                SET status = 'cancelled'
                WHERE id = $1 AND client_tg_id = $2 AND status = 'active'
                RETURNING id, appointment_date, appointment_time
            """, appointment_id, msg.from_user.id)

            if result:
                await conn.execute("""
                    UPDATE schedule 
                    SET available = TRUE
                    WHERE date = $1 AND time = $2
                """, result["appointment_date"], result["appointment_time"])
                
                await msg.answer(
                    "✅ <b>Запись успешно отменена!</b>\n\n"
                    f"Запись #{appointment_id} отменена.\n"
                    f"Если передумаете — будем рады вас записать снова! 💖"
                )
            else:
                await msg.answer(
                    "❌ <b>Запись не найдена</b>\n\n"
                    "Возможно, запись уже отменена или номер указан неверно."
                )