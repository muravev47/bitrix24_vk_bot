import asyncio
from src.parser.bitrix_parser import run_parser
from src.orchestrator import Orchestrator
from src.database.db_manager import init_db

async def prepare():
    print("Инициализация БД...")
    await init_db()
    print("Парсинг документации...")
    await run_parser()
    print("Создание ассистента (это может занять несколько минут)...")
    orch = Orchestrator()
    # Синхронные операции в отдельном потоке
    await asyncio.to_thread(orch.assistant_manager.create_assistant)
    print("✅ База знаний готова! Теперь можно запускать бота: python -m src.main")

if __name__ == "__main__":
    asyncio.run(prepare())