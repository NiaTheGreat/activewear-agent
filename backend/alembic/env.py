import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# Load .env file for local development (no-op in Docker where .env doesn't exist)
load_dotenv()

# Make sure the app package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from app.database import Base
from app.models import User, CriteriaPreset, Search, Manufacturer, ContactActivity  # noqa: F401 – register models

config = context.config

# Use the validated sync URL from Settings (handles Railway's postgres:// format)
db_url = settings.DATABASE_URL_SYNC
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)
else:
    raise RuntimeError(
        "No database URL available. Set DATABASE_URL or DATABASE_URL_SYNC."
    )

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
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
