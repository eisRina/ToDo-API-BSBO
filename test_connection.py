
import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote
from getpass import getpass

load_dotenv(override=True)

try:

    db = urlparse(os.getenv("DATABASE_URL"))

    conn = psycopg2.connect(
        host=db.hostname,
        port=db.port,
        dbname=db.path.lstrip("/"),
        user=unquote(db.username),
        password=getpass("Введите пароль PostgreSQL: "),
        sslmode="require",
        connect_timeout=10
    )


    cursor = conn.cursor()

    cursor.execute("SELECT version();")
    print("Подключение к PostgreSQL успешно!")
    print("Версия БД:", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM public.tasks;")
    print("Количество задач:", cursor.fetchone()[0])

    cursor.close()
    conn.close()

except Exception as error:
    print("Ошибка подключения:", error)
