from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db import db

router = Router()

@router.callback_query(F.data == "my_bookings")
async def my_bookings(cb: CallbackQuery):
    appointments = await db.pool.fetch("""
        SELECT a.id, a.appointment_date, a.appointment_time, p.service_name 
        FROM appointments a
        JOIN price_list p ON a.service_id = p.id
        WHERE a.client_tg_id = $1 AND a.status = 'active'
        ORDER BY a.appointment_date
    """, cb.from_user.id)

    if not appointments:
        await cb.message.edit_text("У вас нет активных записей")
        return

    text = "<b>Ваши записи:</b>\n\n"
    for a in appointments:
        text += f"#{a['id']} — {a['service_name']}\n"
        text += f"{a['appointment_date']} в {str(a['appointment_time'])[:-3]}\n\n"

    text += "Чтобы отменить — просто отправьте номер записи (например: 7)"

    await cb.message.edit_text(text, reply_markup=None)


@router.message(F.text.regexp(r"^\d+$"))
async def cancel_by_number(msg: Message):
    try:
        app_id = int(msg.text.strip())
    except:
        return

    result = await db.pool.fetchrow("""
        UPDATE appointments 
        SET status='cancelled' 
        WHERE id=$1 AND client_tg_id=$2 AND status='active'
        RETURNING appointment_date, appointment_time
    """, app_id, msg.from_user.id)

    if result:
        await db.pool.execute("""
            UPDATE schedule SET available=TRUE, appointment_id=NULL
            WHERE date=$1 AND time=$2
        """, result["appointment_date"], result["appointment_time"])
        await msg.answer(f"Запись #{app_id} успешно отменена")
    else:
        await msg.answer("Запись не найдена или уже отменена")