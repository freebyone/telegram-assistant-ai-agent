import asyncio
from datetime import datetime, timedelta
from db import db
import logging

class ReminderScheduler:
    def __init__(self):
        self.is_running = False
        self.bot = None

    async def start(self, bot_instance):
        """Запускаем планировщик напоминаний"""
        self.bot = bot_instance
        self.is_running = True
        asyncio.create_task(self._reminder_loop())
        print("⏰ Планировщик напоминаний запущен")

    async def stop(self):
        """Останавливаем планировщик"""
        self.is_running = False
        print("⏰ Планировщик напоминаний остановлен")

    async def _reminder_loop(self):
        """Основной цикл отправки напоминаний"""
        while self.is_running:
            try:
                await self._check_and_send_reminders()
                await asyncio.sleep(3600)
            except Exception as e:
                print(f"❌ Ошибка в планировщике: {e}")
                await asyncio.sleep(300)

    async def _check_and_send_reminders(self):
        """Проверяем и отправляем напоминания"""
        try:
            from config import REMINDER_HOURS_BEFORE
            
            appointments = await db.get_upcoming_appointments_for_reminder(
                REMINDER_HOURS_BEFORE
            )
            
            if appointments:
                print(f"🔔 Найдено {len(appointments)} записей для напоминания")
            
            for app in appointments:
                try:
                    message = (
                        "🔔 <b>Напоминание о записи!</b>\n\n"
                        f"У вас запланирован {app['service_name'] or 'сервис'}\n"
                        f"📅 <b>{app['appointment_date'].strftime('%d.%m.%Y')}</b>\n"
                        f"⏰ <b>{str(app['appointment_time'])[:5]}</b>\n\n"
                        "Если вы не можете прийти, пожалуйста, отмените запись."
                    )
                    
                    await self.bot.send_message(
                        app['client_tg_id'],
                        message
                    )
                    
                    await db.mark_reminder_sent(app['id'])
                    print(f"✅ Напоминание отправлено для записи {app['id']}")
                    
                except Exception as e:
                    print(f"❌ Не удалось отправить напоминание {app['id']}: {e}")

        except Exception as e:
            if "column" in str(e) and "does not exist" in str(e):
                pass 
            else:
                print(f"❌ Ошибка при проверке напоминаний: {e}")

scheduler = ReminderScheduler()