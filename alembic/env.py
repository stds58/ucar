import asyncio
import importlib
import pkgutil
import logging
import json
import sys
#from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import settings
from app.models.base import Base


def import_all_models(package_name: str):
    package = importlib.import_module(package_name)
    for _, name, _ in pkgutil.walk_packages(package.__path__, package_name + "."):
        if "models" in name:
            importlib.import_module(name)
            #print("Tables in Base.metadata:", Base.metadata.tables.keys())


import_all_models("app")
# alembic revision --autogenerate -m "Auto-generated migration"
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
sqlalchemy_url = settings.DATABASE_URL
config.set_main_option("sqlalchemy.url", sqlalchemy_url)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        #print("Все поля record:", vars(record))
        parts = []
        if record.exc_info is not None:
            parts.append(f"exc_info: {record.exc_info}")
        if record.exc_text is not None:
            parts.append(f"exc_text: {record.exc_text}")
        if record.stack_info is not None:
            parts.append(f"stack_info: {record.stack_info}")

        # Объединяем в одну строку с переносами, если есть что объединять
        error_str = "\n".join(parts) if parts else None

        return json.dumps({
            "path": record.pathname,
            "timestamp": self.formatTime(record),
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": record.getMessage(),
            "error": error_str,
            "filename": record.filename,
            "func_name": record.funcName,
            "lineno": record.lineno
        }, ensure_ascii=False)


# Настраиваем логгер alembic
alembic_logger = logging.getLogger("alembic")
alembic_logger.setLevel(logging.DEBUG)

# Убираем дублирование, если root logger тоже пишет
alembic_logger.propagate = False

# Добавляем обработчик с JSON-форматтером
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
alembic_logger.addHandler(handler)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    try:
        run_migrations_offline()
    except Exception as e:
        alembic_logger.critical("Alembic migration failed", exc_info=True)
else:
    try:
        run_migrations_online()
    except Exception as e:
        alembic_logger.critical("Alembic migration failed", exc_info=True)
