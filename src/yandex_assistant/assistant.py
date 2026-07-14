import aiohttp
from src.config import settings

class YandexAssistantManager:
    def __init__(self):
        self.api_key = settings.YC_API_KEY
        self.folder_id = settings.YC_FOLDER_ID
        # Актуальный эндпоинт YandexGPT API
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    async def ask_question(self, query: str, history: list = None) -> str:
        """
        Отправляет запрос к Yandex GPT через REST API.
        history: список словарей с ключами "role" и "content"
        """
        messages = []

        # Системная инструкция
        messages.append({
            "role": "system",
            "content": "Ты — эксперт по Bitrix24 API. Отвечай кратко и точно, ссылаясь на документацию."
        })

        # История диалога, если есть
        if history:
            for msg in history:
                role = msg.get("role", "user")
                if role not in ["user", "assistant", "system"]:
                    role = "user"
                messages.append({
                    "role": role,
                    "content": msg.get("content", "")
                })

        # Текущий вопрос
        messages.append({
            "role": "user",
            "content": query
        })

        # Тело запроса
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.1,
                "maxTokens": 2000
            },
            "messages": messages
        }

        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload, headers=headers) as resp:
                data = await resp.json()
                if resp.status != 200:
                    print(f"❌ Yandex API error: {data}")
                    raise Exception(f"Yandex API error (status {resp.status}): {data.get('message', 'Unknown error')}")

                try:
                    answer = data["result"]["alternatives"][0]["message"]["content"]
                except (KeyError, IndexError):
                    raise Exception(f"Unexpected API response: {data}")

                return answer

    async def update_knowledge_base(self, docs_dir: str):
        """
        В этой версии мы не используем поисковые индексы.
        Вся необходимая информация передаётся через системный промпт.
        """
        pass