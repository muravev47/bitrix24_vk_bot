import aiohttp
import asyncio
from bs4 import BeautifulSoup
import aiofiles
import os
from urllib.parse import urljoin, urlparse
from typing import Set, List

BASE_URL = "https://apidocs.bitrix24.ru/"
OUTPUT_DIR = "docs/"


class BitrixParser:
    def __init__(self):
        self.visited = set()  # контроль посещённых URL
        self.stack = []       # очередь на обработку

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        """Загружает HTML страницы."""
        async with session.get(url) as resp:
            return await resp.text()

    def extract_links(self, html: str, base: str) -> List[str]:
        """Извлекает все ссылки на страницы документации."""
        soup = BeautifulSoup(html, "lxml")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base, href)
            # Оставляем только ссылки, ведущие на страницы API (содержат /api-reference/)
            if "/api-reference/" in full_url and full_url not in self.visited:
                links.append(full_url)
        return links

    def extract_content(self, html: str, url: str) -> str:
        """Извлекает текстовое содержимое страницы."""
        soup = BeautifulSoup(html, "lxml")
        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()
        # Ищем заголовок и основное содержимое
        title = soup.find("h1")
        title_text = title.get_text(strip=True) if title else "Без заголовка"
        # Ищем основной контент (можно уточнить селекторы)
        content_div = soup.find("div", class_="content") or soup.find("main") or soup.find("article")
        if content_div:
            text = content_div.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
        return f"# {title_text}\n\n{text}"

    async def save_page(self, url: str, content: str):
        """Сохраняет содержимое в файл."""
        filename = urlparse(url).path.replace("/", "_").strip("_") + ".txt"
        if not filename:
            filename = "index.txt"
        path = os.path.join(OUTPUT_DIR, filename)
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(content)

    async def parse_all(self, start_url: str = BASE_URL):
        """Запускает обход всех страниц."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.stack = [start_url]
        self.visited = set()

        async with aiohttp.ClientSession() as session:
            while self.stack:
                url = self.stack.pop()
                if url in self.visited:
                    continue
                self.visited.add(url)
                print(f"Обработка: {url}")
                try:
                    html = await self.fetch_page(session, url)
                    # Извлекаем содержимое
                    content = self.extract_content(html, url)
                    await self.save_page(url, content)
                    # Находим новые ссылки и добавляем в стек
                    new_links = self.extract_links(html, url)
                    for link in new_links:
                        if link not in self.visited and link not in self.stack:
                            self.stack.append(link)
                except Exception as e:
                    print(f"Ошибка при обработке {url}: {e}")

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url) as resp:
            resp.raise_for_status()  # добавить!
            return await resp.text()

async def run_parser():
    parser = BitrixParser()
    await parser.parse_all()

if __name__ == "__main__":
    asyncio.run(run_parser())