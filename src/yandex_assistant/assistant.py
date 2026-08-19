import asyncio
import pathlib
import os
import json
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.search_indexes import StaticIndexChunkingStrategy, TextSearchIndexType
from src.config import settings


class YandexAssistantManager:
    def __init__(self):
        self.sdk = YCloudML(folder_id=settings.YC_FOLDER_ID, auth=settings.YC_API_KEY)
        self.assistant = None
        self.search_index = None
        self.initialized = False
        self.cache_file = ".yandex_cache"

    def _load_files(self, docs_dir: str):
        """Синхронная загрузка всех текстовых файлов из папки docs_dir."""
        files = []
        docs_path = pathlib.Path(docs_dir)
        if not docs_path.exists():
            raise FileNotFoundError(f"Папка {docs_dir} не найдена. Запустите парсер.")
        for file_path in docs_path.glob("*.txt"):
            with open(file_path, "rb") as f:
                file = self.sdk.files.upload(
                    file_path,
                    ttl_days=7,
                    expiration_policy="static"
                )
                files.append(file)
        return files

    def create_assistant(self, docs_dir: str = "docs/"):
        """
        Синхронное создание (или загрузка из кеша) ассистента и поискового индекса.
        Этот метод вызывается в отдельном потоке, чтобы не блокировать асинхронный цикл.
        """
        if self.initialized:
            return

        # Пытаемся загрузить из кеша
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                assistant_id = data.get("assistant")
                index_id = data.get("search_index")
                if assistant_id and index_id:
                    try:
                        self.assistant = self.sdk.assistants.get(assistant_id)
                        self.search_index = self.sdk.search_indexes.get(index_id)
                        self.initialized = True
                        print("Ассистент загружен из кеша.")
                        return
                    except Exception:
                        print("Кеш недействителен, создаём заново.")
                        os.remove(self.cache_file)

        # Если кеша нет или он повреждён – создаём новые ресурсы
        files = self._load_files(docs_dir)
        if not files:
            raise ValueError("Нет файлов для загрузки. Сначала запустите парсер.")

        print("Создание поискового индекса (это может занять несколько минут)...")
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

        tool = self.sdk.tools.search_index(self.search_index)

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
        # Сохраняем идентификаторы в кеш
        with open(self.cache_file, "w") as f:
            json.dump({
                "assistant": self.assistant.id,
                "search_index": self.search_index.id
            }, f)

        self.initialized = True
        print("Ассистент создан и закеширован.")

    async def ask_question(self, query: str, history: list = None) -> str:
        """
        Асинхронный метод для отправки вопроса ассистенту.
        Создание ассистента (если ещё не создан) и выполнение запроса
        выполняются в отдельных потоках, чтобы не блокировать цикл событий.
        """
        if not self.initialized:
            # Создаём ассистента в отдельном потоке
            await asyncio.to_thread(self.create_assistant)

        # Выполняем запрос в отдельном потоке
        def _run():
            thread = self.sdk.threads.create()
            if history:
                for msg in history:
                    thread.write(msg["content"], role=msg["role"])
            thread.write(query)
            run = self.assistant.run(thread)
            return run.wait().text

        return await asyncio.to_thread(_run)

    async def update_knowledge_base(self, docs_dir: str = "docs/"):
        """Обновляет базу знаний: удаляет кеш и пересоздаёт ассистента."""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        self.initialized = False
        await asyncio.to_thread(self.create_assistant, docs_dir)