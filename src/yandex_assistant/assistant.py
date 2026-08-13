import asyncio
import pathlib
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.search_indexes import StaticIndexChunkingStrategy, TextSearchIndexType
from src.config import settings
import aiofiles
import os

class YandexAssistantManager:
    def __init__(self):
        self.sdk = YCloudML(folder_id=settings.YC_FOLDER_ID, auth=settings.YC_API_KEY)
        self.assistant = None
        self.search_index = None
        self.initialized = False

    async def _load_files(self, docs_dir: str):
        """Загружает все текстовые файлы из docs_dir в File Storage."""
        files = []
        docs_path = pathlib.Path(docs_dir)
        for file_path in docs_path.glob("*.txt"):
            # Загружаем файл в хранилище
            with open(file_path, "rb") as f:
                file = self.sdk.files.upload(
                    file_path,
                    ttl_days=7,
                    expiration_policy="static",
                )
                files.append(file)
        return files

    async def create_assistant(self, docs_dir: str = "docs/"):
        """Создаёт ассистента с поисковым индексом."""
        if self.initialized:
            return

        # Загружаем файлы
        files = await self._load_files(docs_dir)
        if not files:
            raise ValueError("Нет файлов для загрузки. Сначала запустите парсер.")

        # Создаём поисковый индекс
        print("Создание поискового индекса...")
        operation = self.sdk.search_indexes.create_deferred(
            files,
            index_type=TextSearchIndexType(
                chunking_strategy=StaticIndexChunkingStrategy(
                    max_chunk_size_tokens=700,
                    chunk_overlap_tokens=300,
                )
            )
        )
        self.search_index = operation.wait()
        print("Индекс создан.")

        # Создаём инструмент file_search
        tool = self.sdk.tools.search_index(self.search_index)

        # Создаём ассистента с жёстким промптом
        self.assistant = self.sdk.assistants.create(
            'yandexgpt',
            tools=[tool],
            description="Помощник по документации Bitrix24 API",
            instruction=(
                "Ты — эксперт по Bitrix24 API. Отвечай только на основе загруженных документов. "
                "Если информация отсутствует в документах, честно скажи, что не знаешь. "
                "Не выдумывай и не добавляй ничего от себя. Ответы должны быть точными и краткими."
            )
        )
        self.initialized = True
        print("Ассистент создан.")

    async def ask_question(self, query: str, history: list = None) -> str:
        """Задаёт вопрос ассистенту с учётом истории."""
        if not self.initialized:
            await self.create_assistant()

        # Создаём тред для диалога
        thread = self.sdk.threads.create()
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ("user", "assistant"):
                    thread.write(content, role=role)

        thread.write(query)
        run = self.assistant.run(thread)
        result = run.wait()
        return result.text

    async def update_knowledge_base(self, docs_dir: str = "docs/"):
        """Обновляет индекс при появлении новых файлов (пересоздаёт ассистента)."""
        # Удаляем старый индекс и ассистента (опционально)
        if self.search_index:
            # В SDK нет явного удаления, можно просто пересоздать
            pass
        self.initialized = False
        await self.create_assistant(docs_dir)