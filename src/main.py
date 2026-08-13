import asyncio
from src.vk_integration.bot import run_bot
from src.parser.bitrix_parser import run_parser
from src.orchestrator import Orchestrator

async def main():
    # Инициализация оркестратора (создаст ассистента при первом запросе)
    # orchestrator = Orchestrator()
    # Раскомментируйте для первого запуска парсинга:
    # await run_parser()
    # Затем обновите знания:
    # await orchestrator.update_knowledge()

    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())