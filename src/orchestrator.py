from src.database.db_manager import get_or_create_user, save_message, get_history
from src.yandex_assistant.assistant import YandexAssistantManager

class Orchestrator:
    def __init__(self):
        self.assistant_manager = YandexAssistantManager()

    async def get_or_create_user(self, vk_id: int, first_name: str = "", last_name: str = ""):
        return await get_or_create_user(vk_id, first_name, last_name)

    async def process_query(self, user_id: int, query: str) -> str:
        history = await get_history(user_id, limit=5)
        # Преобразуем историю в формат для ассистента
        context = []
        for msg in history:
            # У нас в БД хранятся query и response, но мы не знаем, кто автор.
            # Лучше использовать историю как есть: чередовать user и assistant.
            # Для простоты будем передавать только последние вопросы-ответы.
            # Но так как у нас нет сохранения ролей, сделаем простой вариант:
            # передаём только последние 3 вопроса и ответа (если есть)
            pass  # Здесь можно улучшить
        # Пока передаём пустую историю, но можно доработать.
        answer = await self.assistant_manager.ask_question(query, history=None)
        await save_message(user_id, query, answer)
        return answer

    async def update_knowledge(self):
        """Обновляет базу знаний ассистента."""
        await self.assistant_manager.update_knowledge_base()