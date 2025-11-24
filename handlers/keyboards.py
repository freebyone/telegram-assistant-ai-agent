from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💅 Записаться", callback_data="booking_start")],
        [InlineKeyboardButton(text="💰 Прайс-лист", callback_data="price")],
        [InlineKeyboardButton(text="📅 Свободное время", callback_data="slots")],
        [InlineKeyboardButton(text="📋 Мои записи", callback_data="my_bookings")],
    ])

def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])

def back_to_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ На главную", callback_data="main_menu")]
    ])