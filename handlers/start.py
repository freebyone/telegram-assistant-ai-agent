from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.keyboards import main_menu, cancel_kb
from db import db

router = Router()

@router.message(F.text.in_({"/start", "старт", "привет"}))  # или Command("start")
async def start(message: Message):
    await message.answer(
        "Привет! Я Аня — ваш ассистент по записи в салон красоты\n\n"
        "Чем могу помочь?",
        reply_markup=main_menu()
    )