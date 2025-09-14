from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Create async engine for async operations
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# Create sync engine for migrations and sync operations
sync_engine = create_engine(
    settings.database_url_sync,
    echo=settings.debug,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session factory
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

# Create declarative base
Base = declarative_base()


# Dependency to get async database session
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dependency to get sync database session (for migrations, etc.)
def get_sync_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
