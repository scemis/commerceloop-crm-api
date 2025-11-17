# alembic/env.py
import os, sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# === ВАЖНО: добавить корень проекта в sys.path ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Теперь эти импорты будут находиться
from database import Base              # где объявлен declarative_base()
from config import settings            # где лежит DATABASE_URL

# Конфиг Alembic
config = context.config

# Подменяем sqlalchemy.url на лету из settings
URL_DATABASE = settings.DATABASE_URL
if URL_DATABASE:
    config.set_main_option("sqlalchemy.url", URL_DATABASE)

# Логи
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для автогенерации миграций
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Offline-режим: без подключения, просто генерим SQL."""
    url = URL_DATABASE or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Online-режим: реальное подключение и применение миграций."""
    # engine_from_config читает config, где мы уже подменили sqlalchemy.url
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
