from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.database.models import User, MessageHistory
from src.config import settings
from src.database.models import YandexResource

# Создаем асинхронный engine
DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_user(vk_id: int) -> User | None:
    """Получить пользователя по VK ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.vk_id == vk_id))
        return result.scalar_one_or_none()


async def create_user(vk_id: int, first_name: str = "", last_name: str = "") -> User:
    """Создать нового пользователя."""
    async with AsyncSessionLocal() as session:
        user = User(vk_id=vk_id, first_name=first_name, last_name=last_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_or_create_user(vk_id: int, first_name: str = "", last_name: str = "") -> User:
    """Получить или создать пользователя."""
    user = await get_user(vk_id)
    if user is None:
        user = await create_user(vk_id, first_name, last_name)
    return user


async def save_message(user_id: int, query: str, response: str) -> None:
    """Сохранить историю сообщения."""
    async with AsyncSessionLocal() as session:
        history = MessageHistory(user_id=user_id, query=query, response=response)
        session.add(history)
        await session.commit()


async def get_history(user_id: int, limit: int = 5) -> list[MessageHistory]:
    """Получить историю сообщений пользователя."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MessageHistory)
            .where(MessageHistory.user_id == user_id)
            .order_by(MessageHistory.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

async def save_resource(resource_type: str, resource_id: str):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(YandexResource).where(YandexResource.resource_type == resource_type))
        existing = res.scalar_one_or_none()
        if existing:
            existing.resource_id = resource_id
            existing.updated_at = datetime.utcnow()
        else:
            session.add(YandexResource(resource_type=resource_type, resource_id=resource_id))
        await session.commit()

async def get_resource(resource_type: str) -> str | None:
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(YandexResource).where(YandexResource.resource_type == resource_type))
        obj = res.scalar_one_or_none()
        return obj.resource_id if obj else None