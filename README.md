
# ToDo лист API

## Описание проекта

Учебный проект на FastAPI для управления задачами с использованием матрицы Эйзенхауэра.

Приложение использует облачную базу данных PostgreSQL на платформе Supabase. Взаимодействие с базой реализовано через SQLAlchemy ORM и драйвер psycopg2.

Задачи распределяются по четырём квадрантам:

- Q1 — важные и срочные
- Q2 — важные и несрочные
- Q3 — неважные и срочные
- Q4 — неважные и несрочные

## Используемые технологии

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- Supabase
- SQLAlchemy ORM
- psycopg2
- Pydantic
- python-dotenv
- Git и GitHub

## Возможности API

Версия API: 2.0.0.

### Управление задачами

- GET /api/v2/tasks — получение всех задач
- GET /api/v2/tasks/quadrant/{quadrant} — фильтрация по квадранту
- GET /api/v2/tasks/status/{task_status} — фильтрация по статусу
- GET /api/v2/tasks/search?q=... — поиск задач
- GET /api/v2/tasks/{task_id} — получение задачи по ID
- POST /api/v2/tasks/ — создание задачи
- PUT /api/v2/tasks/{task_id} — обновление задачи
- PATCH /api/v2/tasks/{task_id}/complete — завершение задачи
- DELETE /api/v2/tasks/{task_id} — удаление задачи

### Статистика и служебные запросы

- GET /api/v2/stats — статистика по квадрантам и статусам
- GET /health — проверка подключения к PostgreSQL
- GET / — информация о приложении

## Структура проекта

- main.py — создание приложения и подключение маршрутов
- database.py — настройка подключения к PostgreSQL
- models/task.py — SQLAlchemy-модель задачи
- schemas.py — Pydantic-схемы
- routers/tasks.py — управление задачами
- routers/stats.py — получение статистики
- test_connection.py — тестирование подключения к базе данных
- requirements.txt — зависимости проекта
- .env — локальные настройки подключения (не публикуется)

## Инструкция по запуску

1. Клонировать репозиторий и открыть проект в VS Code.

2. Создать виртуальное окружение:

   python -m venv venv

3. Активировать окружение в PowerShell:

   .\venv\Scripts\Activate.ps1

4. Установить зависимости:

   pip install -r requirements.txt

5. Создать файл .env в корне проекта.

6. Указать переменные окружения:

   DATABASE_URL=postgresql://USERNAME@HOST:5432/postgres
   DB_PASSWORD="YOUR_PASSWORD"

   Вместо шаблонных значений использовать данные подключения к PostgreSQL из Supabase. Пароль не публиковать в репозитории.

7. Запустить приложение:

   uvicorn main:app --reload

8. Открыть документацию Swagger:

   http://127.0.0.1:8000/docs

## Результаты тестирования

Проверена работа API через Swagger UI.

Успешно протестированы операции GET, POST, PUT, PATCH и DELETE.

Проверены поиск, фильтрация, статистика задач и подключение к PostgreSQL.

Все проверенные запросы выполнены успешно.

## Автор

Ролдугина Ирина Олеговна
