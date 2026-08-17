import asyncio
import logging
from src.vk_integration.bot import run_bot
from src.orchestrator import Orchestrator
from src.config import settings
from src.database.db_manager import init_db

logging.basicConfig(level=logging.INFO)

async def main():
    # 1. Проверка конфигурации
    required = ["VK_TOKEN", "VK_GROUP_ID", "YC_API_KEY", "YC_FOLDER_ID", 
                "DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [var for var in required if not getattr(settings, var, None)]
    if missing:
        logging.error(f"Отсутствуют обязательные переменные: {', '.join(missing)}")
        return

    # 2. Инициализация БД (создание таблиц)
    await init_db()

    # 3. Подготовка ассистента (создание/загрузка из кеша)
    logging.info("Подготовка Yandex Assistant...")
    orchestrator = Orchestrator()
    try:
        await orchestrator.assistant_manager.create_assistant()
        logging.info("Ассистент готов.")
    except Exception as e:
        logging.error(f"Ошибка инициализации ассистента: {e}")
        logging.info("Запустите парсер командой: python -m src.parser.bitrix_parser")
        return

    # 4. Запуск бота
    logging.info("Запуск VK бота...")
    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())