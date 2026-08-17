import pathlib
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.search_indexes import StaticIndexChunkingStrategy, TextSearchIndexType
from src.config import settings
from src.database.db_manager import get_resource, save_resource

class YandexAssistantManager:
    def __init__(self):
        self.sdk = YCloudML(folder_id=settings.YC_FOLDER_ID, auth=settings.YC_API_KEY)
        self.assistant = None
        self.search_index = None
        self.initialized = False

    async def _load_files(self, docs_dir: str):
        """Загружает файлы, если их ID не сохранены, и сохраняет ID."""
        file_ids = await get_resource("file_ids")
        if file_ids:
            # Если уже есть сохранённые ID, возвращаем их (можно не перезагружать)
            return file_ids.split(",")
        # Иначе загружаем все файлы
        files = []
        docs_path = pathlib.Path(docs_dir)
        for file_path in docs_path.glob("*.txt"):
            with open(file_path, "rb") as f:
                file = self.sdk.files.upload(file_path, ttl_days=7, expiration_policy="static")
                files.append(file)
        ids = [f.id for f in files]
        await save_resource("file_ids", ",".join(ids))
        return ids

    async def create_assistant(self, docs_dir: str = "docs/"):
        if self.initialized:
            return

        # Получаем сохранённые ID
        assistant_id = await get_resource("assistant")
        index_id = await get_resource("search_index")

        if assistant_id and index_id:
            # Используем существующие
            self.assistant = self.sdk.assistants.get(assistant_id)
            self.search_index = self.sdk.search_indexes.get(index_id)
            self.initialized = True
            return

        # Иначе создаём новые
        file_ids = await self._load_files(docs_dir)
        if not file_ids:
            raise ValueError("Нет файлов для загрузки. Запустите парсер.")

        # Создаём индекс
        print("Создание поискового индекса...")
        operation = self.sdk.search_indexes.create_deferred(
            [self.sdk.files.get(fid) for fid in file_ids],
            index_type=TextSearchIndexType(
                chunking_strategy=StaticIndexChunkingStrategy(
                    max_chunk_size_tokens=700,
                    chunk_overlap_tokens=300,
                )
            )
        )
        self.search_index = operation.wait()
        await save_resource("search_index", self.search_index.id)
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
        await save_resource("assistant", self.assistant.id)
        self.initialized = True
        print("Ассистент создан.")

    async def ask_question(self, query: str, history: list = None) -> str:
        if not self.initialized:
            await self.create_assistant()
        thread = self.sdk.threads.create()
        if history:
            for msg in history:
                thread.write(msg["content"], role=msg["role"])
        thread.write(query)
        run = self.assistant.run(thread)
        result = run.wait()
        return result.text