
import os
from urllib.parse import urlparse, unquote

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в файле .env")

db = urlparse(DATABASE_URL)

# Формируем подключение к PostgreSQL через psycopg2
connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=unquote(db.username),
    password=os.getenv("DB_PASSWORD"),
    host=db.hostname,
    port=db.port,
    database=db.path.lstrip("/")
)

engine = create_engine(
    connection_url,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10
    },
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as session:
        yield session


def init_db():
    # Создаёт отсутствующие таблицы по зарегистрированным моделям.
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована!")
