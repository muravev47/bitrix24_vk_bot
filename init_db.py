import asyncio
from src.database.db_manager import init_db

async def main():
    await init_db()
    print("✅ Таблицы созданы!")

if __name__ == "__main__":
    asyncio.run(main())