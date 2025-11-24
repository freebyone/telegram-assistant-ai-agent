import asyncpg
from config import DATABASE_URL
from datetime import date, timedelta, datetime, time
import asyncio

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def init_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS price_list (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    duration INTEGER
                );

                CREATE TABLE IF NOT EXISTS appointments (
                    id SERIAL PRIMARY KEY,
                    client_tg_id BIGINT NOT NULL,
                    client_name VARCHAR(100),
                    service_id INTEGER REFERENCES price_list(id),
                    appointment_date DATE NOT NULL,
                    appointment_time TIME NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT NOW(),
                    reminder_sent BOOLEAN DEFAULT FALSE
                );

                CREATE TABLE IF NOT EXISTS schedule (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    available BOOLEAN DEFAULT TRUE,
                    appointment_id INTEGER REFERENCES appointments(id),
                    UNIQUE(date, time)
                );
            """)

            if not await conn.fetchval("SELECT COUNT(*) FROM price_list"):
                await conn.executemany(
                    "INSERT INTO price_list (service_name, price, duration) VALUES ($1,$2,$3)",
                    [
                        ("Маникюр + покрытие", 2500, 120),
                        ("Педикюр", 3000, 150),
                        ("Наращивание", 4500, 180),
                        ("Брови", 1500, 60),
                    ]
                )
            print("✅ Таблицы инициализированы")

    async def fill_schedule(self):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM schedule")
            
            start = date.today()
            working_hours = [time(h, 0) for h in range(10, 21)]
            
            for i in range(60):
                current_date = start + timedelta(days=i)
                if current_date.weekday() == 6:
                    continue
                
                for t in working_hours:
                    await conn.execute(
                        "INSERT INTO schedule (date, time) VALUES ($1, $2)",
                        current_date, t
                    )
            print(f"✅ Расписание заполнено на 60 дней вперед ({len(working_hours)} слотов в день)")

    async def get_upcoming_appointments_for_reminder(self, hours_before=24):
        """Получаем записи для отправки напоминаний"""
        target_time = datetime.now() + timedelta(hours=hours_before)
        
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT a.id, a.client_tg_id, a.client_name, a.appointment_date, 
                       a.appointment_time, p.service_name
                FROM appointments a
                LEFT JOIN price_list p ON a.service_id = p.id
                WHERE a.status = 'active' 
                AND a.reminder_sent = FALSE
                AND a.appointment_date = $1
                AND EXTRACT(HOUR FROM a.appointment_time) = $2
            """, target_time.date(), target_time.hour)

    async def mark_reminder_sent(self, appointment_id):
        """Отмечаем, что напоминание отправлено"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE appointments SET reminder_sent = TRUE WHERE id = $1",
                appointment_id
            )

db = Database()