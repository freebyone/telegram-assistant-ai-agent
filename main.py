import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from db import db

from handlers.intent import parse_intent
from handlers.common import show_slots, show_price
from handlers.booking import try_book, cancel_booking

async def handle(msg: Message):
    print(f"Пользователь: {msg.text}")

    intent = await parse_intent(msg.text)
    print("ИИ понял:", intent)

    action = intent.get("action", "unknown")

    if action == "show_slots":
        await show_slots(msg)

    elif action == "show_price":
        await show_price(msg)

    elif action == "book":
        date_str = intent.get("date")
        time_str = intent.get("time")

        if not date_str or not time_str:
            await msg.answer("Укажи дату и время, например: 27 ноября в 15:00")
            return

        await try_book(msg, date_str, time_str)

    elif action == "cancel" and intent.get("appointment_id"):
        await cancel_booking(msg, intent["appointment_id"])

    else:
        await msg.answer("Привет! Я Аня — твой ассистент по записи.\nНапиши, что хочешь — я пойму")

async def main():
    await db.connect()
    await db.init_tables()
    await db.fill_schedule()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.register(handle)

    print("ИИ-АССИСТЕНТ АНЯ ЗАПУЩЕН! Пиши что угодно")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())