import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import aiofiles
import os

async def parse_method_page(url: str, save_path: str) -> str:
    """
    Парсит одну страницу документации метода Bitrix24 и сохраняет в текстовый файл.
    """
    # Настройка Selenium в headless-режиме
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Извлечение данных (структура может отличаться, нужно адаптировать)
        title = soup.find("h1").text.strip() if soup.find("h1") else "No Title"
        description = soup.find("div", class_="description")
        description_text = description.text.strip() if description else "No Description"
        
        # Параметры и примеры - нужно уточнить селекторы
        params = soup.find("div", class_="params")
        params_text = params.text.strip() if params else "No Parameters"
        
        example = soup.find("pre", class_="example")
        example_text = example.text.strip() if example else "No Example"
        
        content = f"# {title}\n\n{description_text}\n\n## Parameters\n\n{params_text}\n\n## Example\n\n{example_text}"
        
        # Асинхронная запись в файл
        async with aiofiles.open(save_path, "w", encoding="utf-8") as f:
            await f.write(content)
        
        return content
    finally:
        driver.quit()


async def parse_all_methods(base_url: str, output_dir: str):
    """
    Парсит все методы API. Здесь нужна логика обхода всех страниц.
    Это заглушка, так как структура сайта требует отдельного анализа.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Пример: список URL для парсинга
    method_urls = [
        "https://apidocs.bitrix24.ru/api-reference/crm/crm-deal-add.html",
        "https://apidocs.bitrix24.ru/api-reference/crm/crm-deal-get.html",
        # ... добавить все нужные URL
    ]
    
    tasks = []
    for url in method_urls:
        filename = url.split("/")[-1].replace(".html", ".txt")
        save_path = os.path.join(output_dir, filename)
        tasks.append(parse_method_page(url, save_path))
    
    await asyncio.gather(*tasks)