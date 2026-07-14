import aiohttp
import asyncio
from src.config import settings
from src.orchestrator import Orchestrator

class VKBot:
    def __init__(self, token: str, group_id: int):
        self.token = token
        self.group_id = group_id
        self.api_url = "https://api.vk.com/method/"
        self.lp_server = None
        self.key = None
        self.ts = None
        self.orchestrator = Orchestrator()

    async def get_long_poll_server(self):
        """Получает сервер для Long Poll API."""
        params = {
            "group_id": self.group_id,
            "access_token": self.token,
            "v": "5.131"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url + "groups.getLongPollServer", params=params) as resp:
                data = await resp.json()
                if "response" in data:
                    self.lp_server = data["response"]["server"]
                    self.key = data["response"]["key"]
                    self.ts = data["response"]["ts"]
                else:
                    raise Exception(f"Ошибка получения Long Poll сервера: {data}")

    async def send_message(self, user_id: int, text: str):
        """Отправляет сообщение пользователю."""
        params = {
            "user_id": user_id,
            "message": text,
            "random_id": 0,
            "access_token": self.token,
            "v": "5.131"
        }
        async with aiohttp.ClientSession() as session:
            await session.get(self.api_url + "messages.send", params=params)

    async def process_updates(self):
        """Основной цикл опроса Long Poll."""
        await self.get_long_poll_server()
        while True:
            url = f"{self.lp_server}?act=a_check&key={self.key}&ts={self.ts}&wait=25"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if "failed" in data:
                        if data["failed"] == 1:
                            self.ts = data["ts"]  # обновляем ts
                        elif data["failed"] == 2:
                            await self.get_long_poll_server()  # перезапрашиваем сервер
                        else:
                            raise Exception("Long Poll ошибка")
                    else:
                        self.ts = data["ts"]
                        for update in data["updates"]:
                            if update["type"] == "message_new":
                                message = update["object"]["message"]
                                # Проверяем, что это личное сообщение (from_id > 0)
                                if message.get("from_id", 0) > 0:
                                    user_id = message["from_id"]
                                    text = message.get("text", "")
                                    if text:
                                        user = await self.orchestrator.get_or_create_user(user_id)
                                        answer = await self.orchestrator.process_query(user.id, text)
                                        await self.send_message(user_id, answer)
            await asyncio.sleep(0.1)

async def run_bot():
    """Запускает бота."""
    bot = VKBot(settings.VK_TOKEN, settings.VK_GROUP_ID)
    await bot.process_updates()