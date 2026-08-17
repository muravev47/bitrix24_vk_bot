import aiohttp
import base64
import os
from src.config import settings

class SpeechRecognizer:
    def __init__(self):
        self.api_key = settings.YC_API_KEY
        self.folder_id = settings.YC_FOLDER_ID
        self.url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

    async def recognize(self, audio_url: str) -> str:
        """Скачивает аудио по URL и распознаёт речь."""
        async with aiohttp.ClientSession() as session:
            # Скачиваем аудиофайл
            async with session.get(audio_url) as resp:
                resp.raise_for_status()
                audio_data = await resp.read()
            # Отправляем в SpeechKit
            headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "x-folder-id": self.folder_id,
                "Content-Type": "audio/ogg"  # или audio/mpeg
            }
            async with session.post(self.url, headers=headers, data=audio_data) as stt_resp:
                stt_resp.raise_for_status()
                result = await stt_resp.json()
                return result.get("result", "")