from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_database_url


DATABASE_URL = get_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")
ENGINE = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 5} if IS_SQLITE else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


class Base(DeclarativeBase):
    pass


if IS_SQLITE:
    @event.listens_for(Engine, "connect")
    def configure_sqlite(connection, _):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
