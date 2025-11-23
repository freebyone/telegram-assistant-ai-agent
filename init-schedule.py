import asyncio
from datetime import date, time, timedelta
from app.database.db import db
from app.config import settings

async def fill_schedule():
    await db.connect()
    async with db.pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM schedule")
        if count > 0:
            print("Расписание уже заполнено")
            return

        start_date = date.today()
        working_hours = [time(h, 0) for h in range(10, 21)]  # 10:00–20:00
        for offset in range(60):  # 60 DAYS
            cur_date = start_date + timedelta(days=offset)
            for t in working_hours:
                await conn.execute(
                    "INSERT INTO schedule (date, time) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                    cur_date, t
                )
        print("Расписание заполнено на 60 дней")

if __name__ == "__main__":
    asyncio.run(fill_schedule())