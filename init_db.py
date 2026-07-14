import asyncio
from src.database.models import Base
from src.database.db_manager import engine

async def init_db():
    async with engine.begin() as conn:
        # Создаём все таблицы, определённые в Base
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(init_db())