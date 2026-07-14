import asyncio
from src.vk_integration.bot import run_bot
from src.parser.bitrix_parser import parse_all_methods
from src.orchestrator import Orchestrator
from src.config import settings

async def main():
    # Инициализация оркестратора
    orchestrator = Orchestrator()
    
    # Парсинг документации (запускается один раз при старте)
    # await parse_all_methods("https://apidocs.bitrix24.ru/", "docs/")
    
    # Обновление базы знаний ассистента
    # await orchestrator.update_knowledge_base("docs/")
    
    # Запуск бота
    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())