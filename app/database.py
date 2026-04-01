from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from app.config import settings
from sqlalchemy.schema import Column, DateTime

engine = create_async_engine(
    url=settings.database_url,
    pool_size=10,
    max_overflow=20,
    echo=settings.environment == "development",
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


class TimeStampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal as session:
        yield session
