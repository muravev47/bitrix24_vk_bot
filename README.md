# octagon-example
# Bitrix24 VK Bot

Бот для консультаций по API Bitrix24 через ВКонтакте с использованием Yandex GPT.

## Установка
1. Клонируйте репозиторий.
2. Создайте виртуальное окружение и установите зависимости: `pip install -r requirements.txt`.
3. Настройте `.env` файл согласно описанию.
4. Выполните `python init_db.py` для создания таблиц в PostgreSQL.
5. Запустите бота: `python -m src.main`.

## Переменные окружения (.env)
- `VK_TOKEN` – токен сообщества ВКонтакте.
- `VK_GROUP_ID` – ID группы (можно с префиксом club).
- `YC_API_KEY` – API-ключ сервисного аккаунта Yandex Cloud.
- `YC_FOLDER_ID` – ID каталога в Yandex Cloud.
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` – параметры подключения к PostgreSQL.