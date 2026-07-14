from src.database.db_manager import get_or_create_user, save_message, get_history
from src.yandex_assistant.assistant import YandexAssistantManager

class Orchestrator:
    def __init__(self):
        self.assistant_manager = YandexAssistantManager()

    async def get_or_create_user(self, vk_id: int, first_name: str = "", last_name: str = ""):
        """Получить или создать пользователя через БД."""
        return await get_or_create_user(vk_id, first_name, last_name)

    async def process_query(self, user_id: int, query: str) -> str:
        """Обработать запрос пользователя."""
        # Получаем историю диалога
        history = await get_history(user_id, limit=5)
        # Преобразуем историю в формат для ассистента
        context = [{"role": "user" if i % 2 == 0 else "assistant", "content": msg.query if i % 2 == 0 else msg.response} for i, msg in enumerate(history)]
        
        # Получаем ответ от ассистента
        answer = await self.assistant_manager.ask_question(query, context)
        
        # Сохраняем историю
        await save_message(user_id, query, answer)
        
        return answer

    async def update_knowledge_base(self, docs_dir: str):
        """Обновляет базу знаний ассистента."""
        await self.assistant_manager.update_knowledge_base(docs_dir)