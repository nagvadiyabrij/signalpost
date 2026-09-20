from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    _upgrade_sqlite_schema()
    # Give a new local install a verified profile from the supplied starter kit.
    # The operation is idempotent and does not overwrite imported/live records.
    from app.seed import seed_starter_data
    db = SessionLocal()
    try:
        seed_starter_data(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _upgrade_sqlite_schema():
    """Apply small idempotent upgrades for existing local SQLite databases."""
    if "sqlite" not in settings.database_url:
        return

    inspector = inspect(engine)
    if "search_history" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("search_history")}
    statements = []
    if "user_id" not in columns:
        statements.append("ALTER TABLE search_history ADD COLUMN user_id VARCHAR(36)")
    if "created_at" not in columns:
        statements.append("ALTER TABLE search_history ADD COLUMN created_at DATETIME")

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
