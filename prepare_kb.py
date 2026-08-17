import asyncio
from src.parser.bitrix_parser import run_parser
from src.orchestrator import Orchestrator
from src.database.db_manager import init_db

async def prepare():
    await init_db()
    print("Парсинг документации...")
    await run_parser()
    print("Создание ассистента...")
    orch = Orchestrator()
    await orch.assistant_manager.create_assistant()
    print("База знаний готова!")

if __name__ == "__main__":
    asyncio.run(prepare())