import aiohttp
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
            async with session.get(audio_url) as resp:
                resp.raise_for_status()
                audio_data = await resp.read()
            # Определяем Content-Type по расширению
            content_type = "audio/mpeg"  # по умолчанию для MP3
            if audio_url.lower().endswith(".ogg"):
                content_type = "audio/ogg"
            elif audio_url.lower().endswith(".wav"):
                content_type = "audio/wav"
            headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "x-folder-id": self.folder_id,
                "Content-Type": content_type
            }
            async with session.post(self.url, headers=headers, data=audio_data) as stt_resp:
                stt_resp.raise_for_status()
                result = await stt_resp.json()
                return result.get("result", "")