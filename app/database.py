from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declared_attr, declarative_base, sessionmaker, Mapped, mapped_column

from app.config import settings


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
