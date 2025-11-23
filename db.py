import asyncpg
from config import DATABASE_URL
from datetime import date, timedelta

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

                CREATE TABLE IF NOT EXISTS schedule (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    available BOOLEAN DEFAULT TRUE,
                    appointment_id INTEGER,
                    UNIQUE(date, time)
                );

                CREATE TABLE IF NOT EXISTS appointments (
                    id SERIAL PRIMARY KEY,
                    client_tg_id BIGINT NOT NULL,
                    client_name VARCHAR(100),
                    service_id INTEGER REFERENCES price_list(id),
                    appointment_date DATE NOT NULL,
                    appointment_time TIME NOT NULL,
                    status VARCHAR(20) DEFAULT 'active'
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

    async def fill_schedule(self):
        async with self.pool.acquire() as conn:
            if await conn.fetchval("SELECT COUNT(*) FROM schedule") > 100:
                return
            start = date.today()
            times = [f"{h:02d}:00" for h in range(10, 21)]
            for i in range(60):
                d = start + timedelta(days=i)
                if d.weekday() == 6: continue
                for t in times:
                    await conn.execute(
                        "INSERT INTO schedule (date, time) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                        d, t
                    )

db = Database()