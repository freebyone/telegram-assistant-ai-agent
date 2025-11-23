from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from db import db

router = Router()

@router.callback_query(F.data == "price")
async def show_price(cb: CallbackQuery):
    prices = await db.pool.fetch("SELECT service_name, price, duration FROM price_list ORDER BY id")
    text = "<b>Прайс-лист</b>\n\n"
    for p in prices:
        text += f"• {p['service_name']} — {p['price']}₽"
        if p['duration']:
            text += f" ({p['duration']} мин)"
        text += "\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Записаться", callback_data="booking_start")]
    ])
    await cb.message.edit_text(text, reply_markup=kb)