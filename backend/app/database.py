from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


# Базовый класс, от которого наследуются все SQLAlchemy-модели.
class Base(DeclarativeBase):
    pass


# Engine и фабрика сессий используют DATABASE_URL из настроек.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    # Dependency для FastAPI: открывает сессию БД на время запроса.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
