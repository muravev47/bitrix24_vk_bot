# Bitrix24 VK Bot (RAG + YandexGPT)

Бот для ВКонтакте, отвечающий на вопросы по документации Bitrix24 API с использованием YandexGPT и RAG.

## 🚀 Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш_логин/bitrix24-vk-bot.git
   cd bitrix24-vk-bot

2. Создайте виртуальное окружение и активируйте его:
    python3.11 -m venv venv
    source venv/bin/activate

3. Установите зависимости:
    pip install -r requirements.txt

4. Создайте файл .env по образцу .env.example и заполните своими данными.

5. Первоначальная подготовка базы знаний (парсинг документации, загрузка в Yandex Cloud, создание индекса):
    python prepare_kb.py  <!-- Этот шаг выполняется один раз перед запуском бота и может занять несколько минут. -->

6. Запустите бота:
    python -m src.main