from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# SQLite veritabanı URL'si
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///deprem.db")

# Async engine oluştur
engine = create_async_engine(DATABASE_URL, echo=True)

# Async session oluştur
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base sınıfı oluştur
Base = declarative_base()

# Async session elde etmek için dependency
async def get_db() -> AsyncSession:
    """
    FastAPI dependency için async session döndürür
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Veritabanını başlat
async def init_db():
    """
    Veritabanını başlatır ve tabloları oluşturur
    """
    async with engine.begin() as conn:
        # Tabloları oluştur
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all) 
