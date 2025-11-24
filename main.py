import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from db import db

async def handle_message(msg: Message):
    print(f"👤 {msg.from_user.full_name}: {msg.text}")

    if msg.text.lower() in ['/start', 'привет', 'начать']:
        from handlers.keyboards import main_menu
        await msg.answer(
            "👋 <b>Привет! Я Аня — ваш ассистент по записи в салон красоты!</b>\n\n"
            "Я понимаю естественную речь, поэтому просто напишите, что хотите:\n"
            "• \"<i>Хочу записаться на маникюр на завтра в 15:00</i>\"\n"
            "• \"<i>Покажи свободное время</i>\"\n"
            "• \"<i>Сколько стоит педикюр?</i>\"\n"
            "• \"<i>Отменить запись 5</i>\"\n\n"
            "Также вы можете использовать кнопки ниже для быстрых действий!",
            reply_markup=main_menu()
        )
        return

    from handlers.intent import parse_intent
    intent = await parse_intent(msg.text)
    print(f"🤖 ИИ определил: {intent}")

    action = intent.get("action", "unknown")

    if action == "show_slots":
        from handlers.common import show_slots
        await show_slots(msg)

    elif action == "show_price":
        from handlers.common import show_price
        await show_price(msg)

    elif action == "book":
        date_str = intent.get("date")
        time_str = intent.get("time")
        service = intent.get("service")

        if not date_str or not time_str:
            await msg.answer(
                "📅 Чтобы записаться, укажите дату и время, например:\n"
                "<i>\"Запиши меня на 27 ноября в 15:00\"</i>\n"
                "<i>\"Хочу маникюр на субботу в 14:30\"</i>"
            )
            return

        from handlers.booking import try_book
        await try_book(msg, date_str, time_str, service)

    elif action == "cancel":
        appointment_id = intent.get("appointment_id")
        if appointment_id:
            from handlers.booking import cancel_booking
            await cancel_booking(msg, appointment_id)
        else:
            await msg.answer(
                "❓ <b>Какую запись хотите отменить?</b>\n\n"
                "Укажите номер записи, например:\n"
                "<i>\"Отменить запись 5\"</i>\n"
                "или посмотрите номер в разделе \"Мои записи\""
            )

    else:
        from handlers.keyboards import main_menu
        await msg.answer(
            "🤔 <b>Я не совсем поняла ваш запрос</b>\n\n"
            "Я могу помочь вам с:\n"
            "• 💅 <b>Записью на услуги</b> (маникюр, педикюр и др.)\n"
            "• 💰 <b>Информацией о ценах</b>\n" 
            "• 📅 <b>Свободным временем</b>\n"
            "• ❌ <b>Отменой записи</b>\n\n"
            "Просто напишите, что вам нужно! 😊",
            reply_markup=main_menu()
        )

async def main():
    global bot_instance
    
    await db.connect()
    await db.init_tables()
    await db.fill_schedule()
    
    # Настройка бота
    bot_instance = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.register(handle_message)

    from scheduler import scheduler
    await scheduler.start(bot_instance)
    print("⏰ Планировщик напоминаний запущен")

    print("✨ ИИ-АССИСТЕНТ АНЯ ЗАПУЩЕН!")
    print("🤖 Бот готов к работе и понимает естественную речь!")
    
    try:
        await dp.start_polling(bot_instance)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
    finally:
        await scheduler.stop()

def get_bot():
    return bot_instance

if __name__ == "__main__":
    asyncio.run(main())