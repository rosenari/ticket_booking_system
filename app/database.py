from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import Config


async_engine = create_async_engine(Config.SQLALCHEMY_DATABASE_URL, echo=True)
session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


# Depends로 여러번 주입해도 동일한 세션 객체가 호출됨. (의존성 캐싱)
async def get_session():
    async with session_factory() as session:
        yield session