import asyncio
import subprocess
from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Type

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from utils.logger_utils import get_shared_logger

logger = get_shared_logger()


class PostgresDatabase:
    def __init__(
        self, db_url: str, enable_log: bool = True, enable_migrations: bool = True
    ):
        self._db_url = db_url
        self._enable_log = enable_log
        self._enable_migrations = enable_migrations
        self._engine = create_async_engine(
            url=self._db_url,
            echo=self._enable_log,
            isolation_level="SERIALIZABLE",
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
            class_=AsyncSession,
        )

        self._scoped_session = async_scoped_session(
            session_factory=self._session_factory, scopefunc=current_task
        )

    @property
    def engine(self):
        return self._engine

    @property
    def scoped_session(self):
        return self._scoped_session

    async def run_migrations(self):
        """Runs Alembic migrations asynchronously."""
        process = await asyncio.create_subprocess_exec(
            "alembic",
            "upgrade",
            "head",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        logger.debug(f"Alembic stdout: {stdout.decode()}")
        logger.debug(f"Alembic stderr: {stderr.decode()}")

        if process.returncode != 0:
            raise RuntimeError(f"Alembic migration failed:\n{stderr.decode().strip()}")

    async def initialize_db(self, declarative_base: Type[DeclarativeBase]):
        """Initializes the database with migrations or schema creation."""
        if self._enable_migrations:
            await self.run_migrations()
        else:
            async with self._engine.begin() as connection:
                await connection.run_sync(declarative_base.metadata.create_all)
            await self._engine.dispose()

    async def close(self):
        if self._scoped_session:
            await self._scoped_session.aclose()
        if self._engine:
            await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provides a session scope with automatic cleanup."""
        session = self._session_factory()
        try:
            yield session
        finally:
            await session.close()
