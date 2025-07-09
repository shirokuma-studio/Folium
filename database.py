from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging

logger = logging.getLogger('discord')

# Baseはmodels.pyからインポートするように変更
from models import Base

class Database:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False) # echo=TrueでSQLログを出力
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized and tables created.")

    async def get_session(self) -> AsyncSession:
        return self.async_session()
