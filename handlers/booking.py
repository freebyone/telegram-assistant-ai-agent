from aiogram.types import Message
from db import db
from datetime import datetime, time

async def try_book(msg: Message, date_str: str, time_str: str):
    try:
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(time_str, "%H:%M").time()
    except:
        await msg.answer("Не поняла дату или время")
        return

    async with db.pool.acquire() as conn:
        async with conn.transaction():
            app_id = await conn.fetchval("""
                INSERT INTO appointments 
                (client_tg_id, client_name, appointment_date, appointment_time)
                VALUES ($1, $2, $3, $4) RETURNING id
            """, msg.from_user.id, msg.from_user.full_name, appointment_date, appointment_time)

            updated = await conn.execute("""
                UPDATE schedule 
                SET available = FALSE
                WHERE date = $1 AND time = $2 AND available = TRUE
            """, appointment_date, appointment_time)

            if updated == "UPDATE 1":
                await msg.answer(
                    f"ГОТОВО! Ты записан(а)\n\n"
                    f"{appointment_date.strftime('%d.%m')} в {time_str}\n"
                    f"Номер записи: <b>#{app_id}</b>\n\n"
                    f"Для отмены пришли этот номер"
                )
            else:
                await conn.execute("DELETE FROM appointments WHERE id = $1", app_id)
                await msg.answer("Это время уже занято. Вот свободные:")
                from .common import show_slots
                await show_slots(msg)

async def cancel_booking(msg: Message, appointment_id: int):
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            result = await conn.fetchrow("""
                UPDATE appointments 
                SET status = 'cancelled'
                WHERE id = $1 AND client_tg_id = $2 AND status = 'active'
                RETURNING appointment_date, appointment_time
            """, appointment_id, msg.from_user.id)

            if result:
                await conn.execute("""
                    UPDATE schedule 
                    SET available = TRUE
                    WHERE date = $1 AND time = $2
                """, result["appointment_date"], result["appointment_time"])
                await msg.answer(f"Запись #{appointment_id} успешно отменена!")
            else:
                await msg.answer("Запись не найдена или уже отменена")