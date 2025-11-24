import asyncio
from db import db

async def reset_database():
    print("🔄 Сбрасываем базу данных...")
    
    await db.connect()
    
    try:
        async with db.pool.acquire() as conn:
            await conn.execute("DROP TABLE IF EXISTS schedule, appointments, price_list CASCADE")
            print("🗑️ Старые таблицы удалены")
        
        await db.init_tables()
        await db.fill_schedule()
        print("✅ База данных успешно пересоздана")
        
    except Exception as e:
        print(f"❌ Ошибка при сбросе БД: {e}")
    finally:
        await db.pool.close()

if __name__ == "__main__":
    asyncio.run(reset_database())