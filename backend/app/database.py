# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Load database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in environment variables")

# Async engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Base model class
Base = declarative_base()

# Async session factory (replaces SessionLocal)
async_session_factory = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency to get a database session
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logging.error(f"Database session error: {e}")
            await session.rollback()
        finally:
            await session.close()

# Database initialization
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("✅ Database initialized successfully")

# Allow manual CLI init (optional)
if __name__ == "__main__":
    asyncio.run(init_db())
    print("✅ Database initialized successfully")