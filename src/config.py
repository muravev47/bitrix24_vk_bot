import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    VK_TOKEN = os.getenv("VK_TOKEN")
    VK_GROUP_ID = int(os.getenv("VK_GROUP_ID", 0))
    YC_API_KEY = os.getenv("YC_API_KEY")
    YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "bitrix_bot")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

settings = Settings()