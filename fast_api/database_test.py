import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/api_demo_db"


async def test_connection():
    engine = create_async_engine(DATABASE_URL, echo=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Connection successful")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await engine.dispose()


asyncio.run(test_connection())
