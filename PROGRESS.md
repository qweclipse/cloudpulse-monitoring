# CloudPulse Progress

## Этап 0 - Initial project structure

Что создано:

- Создана начальная monorepo-структура проекта.
- Добавлены директории `backend/`, `frontend/`, `k8s/`, `.github/workflows/`.
- Создан root `README.md` с кратким описанием проекта, сервисов и планируемой архитектуры.
- Создан `.gitignore` для Python, Node/Vite, локальных env-файлов и временных артефактов.
- Добавлены placeholder README файлы в `backend/` и `frontend/`.
- Добавлены `.gitkeep` файлы в пустые директории `k8s/` и `.github/workflows/`.

Измененные файлы:

- `README.md`
- `.gitignore`
- `backend/README.md`
- `frontend/README.md`
- `k8s/.gitkeep`
- `.github/workflows/.gitkeep`
- `PROGRESS.md`

Как проверить:

- Убедиться, что в корне проекта есть `README.md`, `.gitignore` и `PROGRESS.md`.
- Убедиться, что существуют директории `backend/`, `frontend/`, `k8s/`, `.github/workflows/`.
- Открыть `README.md` и проверить, что в нем описаны цель проекта, основные сервисы и планируемая архитектура.

Ограничения:

- Бизнес-логика пока не реализована.
- Backend, frontend, Docker, Kubernetes и CI/CD будут добавляться на следующих этапах.

## Этап 1 - Backend skeleton

Что создано:

- Создано базовое FastAPI-приложение в `backend/app/main.py`.
- Добавлен endpoint `GET /health`, который возвращает `{"status": "ok"}`.
- Созданы базовые файлы `config.py`, `database.py`, `models.py`, `schemas.py`.
- Созданы пакеты `routes/` и `services/` для будущего разделения API и бизнес-логики.
- Создан `backend/requirements.txt` с зависимостями FastAPI, Uvicorn и pydantic-settings.
- Обновлен `backend/README.md` с инструкцией локального запуска.

Измененные файлы:

- `backend/README.md`
- `backend/requirements.txt`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/routes/__init__.py`
- `backend/app/services/__init__.py`
- `PROGRESS.md`

Как проверить:

- Выполнить команды:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Открыть `http://localhost:8000/health`.
- Ожидаемый ответ: `{"status":"ok"}`.
- Проверено локально через `uvicorn app.main:app`: endpoint `/health` вернул `{"status":"ok"}`.

Ограничения:

- Подключение к PostgreSQL еще не реализовано.
- CRUD API, модели данных, worker, scheduler и frontend будут добавлены на следующих этапах.

## Этап 2 - PostgreSQL support and database models

Что создано:

- Добавлены зависимости `SQLAlchemy` и `psycopg[binary]` в `backend/requirements.txt`.
- В `backend/app/config.py` добавлена настройка `database_url`, читаемая из переменной окружения `DATABASE_URL`.
- В `backend/app/database.py` создан SQLAlchemy `Base`, engine, `SessionLocal` и dependency `get_db()`.
- В `backend/app/models.py` добавлены модели `Monitor`, `CheckResult`, `Incident`.
- Добавлены enum'ы `MonitorStatus`, `CheckStatus`, `IncidentStatus`.
- Создан пример `backend/.env.example` для настройки подключения к PostgreSQL.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/.env.example`
- `backend/requirements.txt`
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/app/models.py`
- `PROGRESS.md`

Как проверить:

- Установить зависимости:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

- Проверить импорт приложения и моделей:

```powershell
python -c "from app.main import app; from app.models import Monitor, CheckResult, Incident; from app.config import settings; print(settings.database_url); print(app.title)"
```

- Убедиться, что `DATABASE_URL` можно переопределить через environment variable или файл `.env`.
- Проверено локально: импорт приложения и моделей прошел успешно, `Base.metadata` содержит таблицы `monitors`, `check_results`, `incidents`.
- Проверено локально: переопределение `DATABASE_URL` через environment variable работает.
- Проверено локально через `uvicorn app.main:app`: endpoint `/health` по-прежнему возвращает `{"status":"ok"}`.

Ограничения:

- Таблицы в PostgreSQL пока не создаются автоматически.
- Alembic migrations будут добавлены на следующем этапе.
- CRUD API для monitor'ов еще не реализован.

## Этап 3 - Alembic migrations

Что создано:

- Добавлена зависимость `alembic` в `backend/requirements.txt`.
- Создан `backend/alembic.ini`.
- Создан Alembic environment в `backend/alembic/env.py`.
- Alembic настроен на чтение `DATABASE_URL` через `app.config.settings`.
- Создана initial migration `backend/alembic/versions/0001_initial_schema.py`.
- Миграция создает таблицы `monitors`, `check_results`, `incidents`.
- Миграция создает enum types `monitor_status`, `check_status`, `incident_status`.
- Обновлены `README.md` и `backend/README.md` командами для миграций.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/requirements.txt`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/0001_initial_schema.py`
- `PROGRESS.md`

Как проверить:

- Установить зависимости:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

- Проверить, что Alembic видит ревизию:

```powershell
alembic heads
```

- Применить миграцию к запущенному PostgreSQL:

```powershell
alembic upgrade head
```

- Без запущенного PostgreSQL можно проверить генерацию SQL:

```powershell
alembic upgrade head --sql
```

- Проверено локально: `alembic heads` показывает `0001_initial_schema (head)`.
- Проверено локально: `alembic upgrade head --sql` успешно генерирует SQL для enum types, таблиц, индексов и `alembic_version`.
- Проверено локально: импорт приложения и SQLAlchemy metadata по-прежнему работает.

Ограничения:

- Локальный PostgreSQL сервис в проекте еще не добавлен, он появится на Docker Compose этапах.
- CRUD API для monitor'ов еще не реализован.

## Этап 4 - Monitor CRUD API

Что создано:

- Добавлены Pydantic schemas для monitor'ов в `backend/app/schemas.py`.
- Реализован CRUD service слой в `backend/app/services/crud.py`.
- Добавлен router `backend/app/routes/monitors.py`.
- В `backend/app/main.py` подключены endpoints:
  - `GET /monitors`
  - `POST /monitors`
  - `GET /monitors/{monitor_id}`
  - `PUT /monitors/{monitor_id}`
  - `DELETE /monitors/{monitor_id}`
- Добавлена валидация URL через Pydantic `AnyHttpUrl`.
- При создании monitor по умолчанию устанавливается `current_status = UNKNOWN`, `is_active = true`.
- Для отсутствующего monitor возвращается `404 Monitor not found`.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/routes/monitors.py`
- `backend/app/services/crud.py`
- `PROGRESS.md`

Как проверить:

- Установить зависимости:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

- Применить миграции к запущенному PostgreSQL:

```powershell
alembic upgrade head
```

- Запустить backend:

```powershell
uvicorn app.main:app --reload
```

- Открыть Swagger UI:

```text
http://localhost:8000/docs
```

- Проверить создание, получение списка, получение по id, обновление и удаление monitor'а.
- Проверено локально: приложение импортируется, OpenAPI содержит `/monitors` и `/monitors/{monitor_id}`.
- Проверено локально: CRUD service flow проходит на временной SQLite базе.
- Проверено локально: route для отсутствующего monitor возвращает `404 Monitor not found`.

Ограничения:

- Для реальной проверки через Swagger нужен запущенный PostgreSQL и выполненный `alembic upgrade head`.
- Manual check endpoint и логика проверки сайтов будут добавлены на следующих этапах.

## Этап 5 - Website checking logic

Что создано:

- Добавлена зависимость `httpx` в `backend/requirements.txt`.
- Создан сервис `backend/app/services/checker.py`.
- Реализована функция `check_monitor(db, monitor_id) -> CheckResult`.
- `check_monitor` загружает monitor из базы, выполняет HTTP `GET`, измеряет latency и сохраняет `CheckResult`.
- При успешной проверке устанавливаются `CheckResult.status = SUCCESS` и `Monitor.current_status = UP`.
- При ошибке устанавливаются `CheckResult.status = FAILED` и `Monitor.current_status = DOWN`.
- Обрабатываются timeout, connection errors, invalid URLs и unexpected status code.
- Обновляется `Monitor.last_checked_at`.
- Добавлен `MonitorNotFoundError` для отсутствующего monitor'а.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/requirements.txt`
- `backend/app/services/checker.py`
- `PROGRESS.md`

Как проверить:

- Установить зависимости:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

- Временный прямой вызов функции после создания monitor'а:

```powershell
python -c "from app.database import SessionLocal; from app.services.checker import check_monitor; db = SessionLocal(); print(check_monitor(db, 1).status); db.close()"
```

- Проверено локально на временной SQLite базе:
  - успешный HTTP response создает `SUCCESS` и переводит monitor в `UP`;
  - unexpected status code создает `FAILED` и переводит monitor в `DOWN`;
  - connection error создает `FAILED` без `status_code`;
  - invalid URL создает `FAILED` с понятным `error_message`;
  - отсутствующий monitor вызывает `MonitorNotFoundError`.

Ограничения:

- Ручной endpoint `POST /monitors/{monitor_id}/check` еще не добавлен.
- Incident management пока не подключен, он будет добавлен на следующих этапах.

## Этап 6 - Manual check endpoint

Что создано:

- Добавлена schema `CheckResultRead` в `backend/app/schemas.py`.
- Добавлен endpoint `POST /monitors/{monitor_id}/check` в `backend/app/routes/monitors.py`.
- Endpoint вызывает `check_monitor(db, monitor_id)`.
- Endpoint возвращает созданный `CheckResult`.
- Для отсутствующего monitor возвращается `404 Monitor not found`.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/app/schemas.py`
- `backend/app/routes/monitors.py`
- `PROGRESS.md`

Как проверить:

- Запустить PostgreSQL и применить миграции:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

- Запустить backend:

```powershell
uvicorn app.main:app --reload
```

- Открыть Swagger UI:

```text
http://localhost:8000/docs
```

- Создать monitor через `POST /monitors`.
- Вызвать `POST /monitors/{monitor_id}/check`.
- Проверить, что ответ содержит `CheckResult`.
- Проверить через `GET /monitors/{monitor_id}`, что `current_status` и `last_checked_at` обновились.
- Проверено локально через `TestClient`: endpoint возвращает `CheckResult`, обновляет monitor и возвращает 404 для отсутствующего monitor.

Ограничения:

- Incident management пока не подключен.
- Автоматические проверки через worker/scheduler будут добавлены позже.

## Этап 7 - Incident management logic

Что создано:

- Создан сервис `backend/app/services/incident_service.py`.
- Реализовано создание `OPEN` incident при failed check.
- Реализована защита от дубликатов: повторный failed check не создает второй `OPEN` incident для того же monitor.
- Реализовано закрытие `OPEN` incident при successful check.
- При закрытии incident устанавливаются `status = RESOLVED`, `resolved_at`, `duration_seconds`.
- В `reason` сохраняется причина падения из `CheckResult.error_message` или fallback-сообщение.
- `incident_service.handle_check_result(...)` подключен внутри `check_monitor(...)`.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/app/services/checker.py`
- `backend/app/services/incident_service.py`
- `PROGRESS.md`

Как проверить:

- Запустить PostgreSQL, применить миграции и backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload
```

- Создать monitor, который возвращает unexpected status code или недоступен.
- Вызвать `POST /monitors/{monitor_id}/check`.
- Проверить в базе, что создан один `OPEN` incident.
- Повторить failed check и убедиться, что дубликат incident не создан.
- Сделать monitor успешным и повторить check.
- Проверить, что incident закрыт: `status = RESOLVED`, заполнены `resolved_at` и `duration_seconds`.
- Проверено локально на временной SQLite базе: failed check создает incident, повторный failed check не создает дубликат, successful check закрывает incident.

Ограничения:

- API для просмотра incidents будет добавлен на следующем этапе.
- Автоматические проверки через worker/scheduler будут добавлены позже.

## Этап 8 - Checks, incidents and stats API

Что создано:

- Добавлены schemas `MonitorSummary`, `IncidentRead`, `StatsRead` в `backend/app/schemas.py`.
- Создан read-only service `backend/app/services/queries.py`.
- Добавлен endpoint `GET /monitors/{monitor_id}/checks`.
- Добавлен endpoint `GET /monitors/{monitor_id}/incidents`.
- Добавлен endpoint `GET /incidents`.
- Для `GET /incidents` добавлен optional query filter `status=OPEN|RESOLVED`.
- Добавлен endpoint `GET /stats`.
- `GET /stats` возвращает:
  - `total_monitors`
  - `up_monitors`
  - `down_monitors`
  - `unknown_monitors`
  - `active_incidents`
  - `average_latency_ms`
- Incidents responses включают краткий nested monitor summary.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/routes/monitors.py`
- `backend/app/routes/incidents.py`
- `backend/app/routes/stats.py`
- `backend/app/services/queries.py`
- `PROGRESS.md`

Как проверить:

- Запустить PostgreSQL, применить миграции и backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload
```

- Создать несколько monitors через `POST /monitors`.
- Запустить проверки через `POST /monitors/{monitor_id}/check`.
- Проверить:

```text
GET /stats
GET /monitors/{monitor_id}/checks
GET /monitors/{monitor_id}/incidents
GET /incidents
GET /incidents?status=OPEN
```

- Проверено локально через `TestClient` на временной SQLite базе:
  - `/monitors/{monitor_id}/checks` возвращает историю свежими проверками первыми;
  - `/monitors/{monitor_id}/incidents` возвращает incidents с monitor summary;
  - `/incidents` возвращает общий список incidents;
  - `/incidents?status=OPEN` фильтрует только открытые incidents;
  - `/stats` корректно считает monitors по статусам, active incidents и average latency;
  - отсутствующий monitor для history endpoints возвращает 404.

Ограничения:

- Frontend для отображения этих данных будет добавлен позже.
- Автоматические проверки через worker/scheduler будут добавлены позже.

## Этап 9 - Docker support for backend and PostgreSQL

Что создано:

- Создан `backend/Dockerfile` для FastAPI backend.
- Создан `backend/.dockerignore`, чтобы не копировать `.venv`, cache и локальные env-файлы в image.
- Создан root `docker-compose.yml`.
- В Docker Compose добавлен service `api`.
- В Docker Compose добавлен service `postgres`.
- Для `api` настроен `DATABASE_URL` на PostgreSQL service внутри Compose.
- Для `api` настроен порт `8000:8000`.
- Для `api` добавлен healthcheck через `GET /health`.
- Для `postgres` настроены `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
- Для `postgres` добавлен volume `postgres_data`.
- Для `postgres` добавлен healthcheck через `pg_isready`.
- `api` ждет healthy PostgreSQL, выполняет `alembic upgrade head`, затем запускает Uvicorn.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/Dockerfile`
- `backend/.dockerignore`
- `docker-compose.yml`
- `PROGRESS.md`

Как проверить:

```powershell
docker compose up --build
```

Открыть:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Ожидаемый результат:

- `GET /health` возвращает `{"status":"ok"}`.
- Swagger UI доступен на `/docs`.
- PostgreSQL container healthy.
- API container применяет Alembic migration перед стартом.
- Проверено локально: `docker compose config` успешно валидирует compose файл.
- Проверено локально: backend по-прежнему компилируется и импортируется, `alembic heads` показывает `0001_initial_schema (head)`.

Ограничения:

- В Compose пока есть только `api` и `postgres`.
- Redis, worker, scheduler и frontend services будут добавлены на следующих этапах.
- Полноценный `docker compose up --build` не был завершен в текущем окружении, потому что Docker daemon недоступен: `//./pipe/docker_engine` не найден. Нужно запустить Docker Desktop или Rancher Desktop и повторить команду.

## Этап 10 - Redis queue support

Что создано:

- Добавлена зависимость `redis` в `backend/requirements.txt`.
- В `backend/app/config.py` добавлены настройки `redis_url` и `redis_queue_name`.
- Обновлен `backend/.env.example` переменными `REDIS_URL` и `REDIS_QUEUE_NAME`.
- Создан сервис `backend/app/services/queue.py`.
- Реализована функция `enqueue_monitor_check(monitor_id)`.
- Реализована функция `dequeue_monitor_check()`.
- В `docker-compose.yml` добавлен service `redis`.
- Для `redis` добавлен healthcheck через `redis-cli ping`.
- Для `api` добавлен `REDIS_URL` и `REDIS_QUEUE_NAME`.
- `api` теперь ожидает healthy `postgres` и healthy `redis`.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/.env.example`
- `backend/requirements.txt`
- `backend/app/config.py`
- `backend/app/services/queue.py`
- `docker-compose.yml`
- `PROGRESS.md`

Как проверить:

```powershell
docker compose up --build
```

Затем можно проверить API:

```text
http://localhost:8000/health
```

И отдельно проверить queue helpers при запущенном Redis:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -c "from app.services.queue import enqueue_monitor_check, dequeue_monitor_check; enqueue_monitor_check(1); print(dequeue_monitor_check())"
```

Ожидаемый результат:

- Redis container healthy.
- `enqueue_monitor_check(1)` кладет задачу в Redis list queue.
- `dequeue_monitor_check()` возвращает `1`.
- Проверено локально: `docker compose config --quiet` валидирует Compose файл.
- Проверено локально: нормализованный `docker compose config` содержит `redis`, `REDIS_URL`, порт `6379` и `redis-cli` healthcheck.
- Проверено локально: queue helpers работают с fake Redis client без внешнего Redis.
- Проверено локально: backend по-прежнему запускается через Uvicorn, `/health` возвращает `{"status":"ok"}`.

Ограничения:

- В текущем окружении Docker daemon недоступен, поэтому полный `docker compose up --build` нужно повторить после запуска Docker Desktop или Rancher Desktop.
- Worker, scheduler и автоматическая обработка задач будут добавлены на следующих этапах.

## Этап 11 - Worker service

Что создано:

- В `backend/app/services/queue.py` добавлена поддержка blocking dequeue через Redis `BLPOP`.
- В `backend/app/config.py` добавлена настройка `worker_queue_timeout_seconds`.
- В `backend/.env.example` добавлена переменная `WORKER_QUEUE_TIMEOUT_SECONDS`.
- Создан `backend/app/worker.py`.
- Worker подключается к Redis.
- Worker подключается к PostgreSQL через `SessionLocal`.
- Worker ждет задачи из Redis queue.
- Worker берет `monitor_id` и вызывает `check_monitor(db, monitor_id)`.
- Worker логирует успешные проверки, отсутствующие monitor'ы и ошибки задач.
- Ошибка одной задачи не останавливает worker loop.
- В `docker-compose.yml` добавлен service `worker`.
- `worker` использует тот же backend image `cloudpulse-backend:local`.
- `worker` запускается командой `python -m app.worker`.
- `worker` ждет healthy `postgres`, `redis` и `api`.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/.env.example`
- `backend/app/config.py`
- `backend/app/services/queue.py`
- `backend/app/worker.py`
- `docker-compose.yml`
- `PROGRESS.md`

Как проверить:

```powershell
docker compose up --build
```

После запуска создать monitor через API, затем положить задачу:

```powershell
docker compose exec api python -c "from app.services.queue import enqueue_monitor_check; enqueue_monitor_check(1)"
```

Проверить worker logs:

```powershell
docker compose logs -f worker
```

Ожидаемый результат:

- Worker получает `monitor_id` из Redis.
- Worker вызывает `check_monitor`.
- В базе появляется `CheckResult`.
- `Monitor.current_status` и `last_checked_at` обновляются.
- Ошибка одной задачи логируется, но worker продолжает работать.
- Проверено локально: `docker compose config --quiet` валидирует Compose файл.
- Проверено локально: blocking dequeue работает с fake Redis client.
- Проверено локально: worker `process_monitor_check` обрабатывает задачу на временной SQLite базе.
- Проверено локально: backend по-прежнему запускается через Uvicorn, `/health` возвращает `{"status":"ok"}`.

Ограничения:

- В текущем окружении Docker daemon недоступен, поэтому полный `docker compose up --build` нужно повторить после запуска Docker Desktop или Rancher Desktop.
- Scheduler service будет добавлен на следующем этапе.

## Этап 12 - Scheduler service

Что создано:

- В `backend/app/config.py` добавлена настройка `scheduler_poll_interval_seconds`.
- В `backend/.env.example` добавлена переменная `SCHEDULER_POLL_INTERVAL_SECONDS`.
- В `backend/app/services/queue.py` добавлена проверка `is_monitor_check_queued(monitor_id)`.
- `enqueue_monitor_check(...)` получил option `skip_if_queued`.
- Создан `backend/app/scheduler.py`.
- Scheduler каждые 10 секунд находит active monitors.
- Scheduler добавляет задачу, если `last_checked_at = null`.
- Scheduler добавляет задачу, если `now - last_checked_at >= interval_seconds`.
- Scheduler пропускает inactive monitors.
- Scheduler не добавляет дубликат, если monitor уже есть в Redis list queue.
- В `docker-compose.yml` добавлен service `scheduler`.
- `scheduler` использует тот же backend image `cloudpulse-backend:local`.
- `scheduler` запускается командой `python -m app.scheduler`.
- `scheduler` ждет healthy `postgres`, `redis` и `api`.
- Обновлены `README.md` и `backend/README.md`.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/.env.example`
- `backend/app/config.py`
- `backend/app/services/queue.py`
- `backend/app/scheduler.py`
- `docker-compose.yml`
- `PROGRESS.md`

Как проверить:

```powershell
docker compose up --build
```

Создать active monitor через API. Подождать `interval_seconds` или создать monitor без `last_checked_at`.

Проверить scheduler logs:

```powershell
docker compose logs -f scheduler
```

Проверить worker logs:

```powershell
docker compose logs -f worker
```

Ожидаемый результат:

- Scheduler добавляет due monitor ids в Redis queue.
- Worker забирает задачи и создает `CheckResult`.
- `Monitor.current_status` и `last_checked_at` обновляются.
- Scheduler не добавляет дубликат задачи, если monitor уже ожидает в Redis queue.
- Проверено локально: `docker compose config --quiet` валидирует Compose файл.
- Проверено локально: Compose содержит `scheduler`, `python -m app.scheduler`, `SCHEDULER_POLL_INTERVAL_SECONDS`.
- Проверено локально на временной SQLite базе: scheduler выбирает due active monitors, пропускает inactive/fresh monitors и не создает дубликаты в fake Redis queue.
- Проверено локально: backend по-прежнему запускается через Uvicorn, `/health` возвращает `{"status":"ok"}`.

Ограничения:

- В текущем окружении Docker daemon недоступен, поэтому полный `docker compose up --build` нужно повторить после запуска Docker Desktop или Rancher Desktop.
- Frontend будет добавлен позже.

## Этап 13 - Frontend skeleton

Что создано:

- Создан React + Vite frontend project в `frontend/`.
- Добавлен `frontend/package.json`.
- Добавлен `frontend/index.html`.
- Добавлен `frontend/vite.config.js`.
- Добавлен `frontend/.env.example` с `VITE_API_BASE_URL`.
- Создан `frontend/src/main.jsx`.
- Создан `frontend/src/App.jsx` с базовым routing.
- Создан shared layout `frontend/src/layout/AppLayout.jsx`.
- Созданы страницы:
  - `frontend/src/pages/Dashboard.jsx`
  - `frontend/src/pages/AddMonitor.jsx`
  - `frontend/src/pages/MonitorDetails.jsx`
  - `frontend/src/pages/Incidents.jsx`
- Создан API client module `frontend/src/api/client.js`.
- Добавлен простой responsive CSS в `frontend/src/styles.css`.
- Обновлены `README.md` и `frontend/README.md`.

Измененные файлы:

- `README.md`
- `frontend/README.md`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/index.html`
- `frontend/vite.config.js`
- `frontend/.env.example`
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/api/client.js`
- `frontend/src/layout/AppLayout.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/pages/AddMonitor.jsx`
- `frontend/src/pages/MonitorDetails.jsx`
- `frontend/src/pages/Incidents.jsx`
- `frontend/src/styles.css`
- `PROGRESS.md`

Как проверить:

```powershell
cd frontend
npm install
npm run dev
```

Открыть:

```text
http://127.0.0.1:5173
```

Проверить:

- Навигация между Dashboard, Add Monitor и Incidents работает.
- Route `monitors/:monitorId` открывает Monitor Details page.
- Frontend build проходит:

```powershell
npm run build
```

- Проверено локально: `npm install` успешно установил зависимости без vulnerabilities.
- Проверено локально: `npm run build` успешно собрал frontend.
- Проверено локально: Vite dev server запущен на `http://127.0.0.1:5173` и отвечает `200`.

Ограничения:

- Dashboard пока содержит skeleton UI без загрузки реальных backend данных.
- Add Monitor form пока не отправляет данные в backend.
- Details и Incidents pages пока без полной интеграции с backend API.

## Этап 14 - Dashboard page

Что создано:

- Dashboard подключен к backend API.
- Добавлена загрузка `GET /stats` для карточек Total, UP, DOWN, UNKNOWN, Active incidents и Average latency.
- Добавлена загрузка `GET /monitors` для таблицы monitor'ов.
- Для каждого monitor'а подтягивается последняя проверка через `GET /monitors/{monitor_id}/checks`.
- В таблице отображаются Name, URL, Status, Last checked, Latency и Actions.
- Добавлены действия View details, Run manual check, Enable/Disable и Delete.
- Manual check вызывает `POST /monitors/{monitor_id}/check`, после чего Dashboard обновляет данные.
- Enable/Disable вызывает `PUT /monitors/{monitor_id}` с `is_active`.
- Delete вызывает `DELETE /monitors/{monitor_id}`, после чего Dashboard обновляет список.
- Добавлены inline сообщения об ошибках и успешных действиях.
- Backend получил CORS-настройку для стандартных Vite origins.

Измененные файлы:

- `README.md`
- `frontend/README.md`
- `backend/.env.example`
- `backend/app/config.py`
- `backend/app/main.py`
- `frontend/src/api/client.js`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/styles.css`
- `PROGRESS.md`

Как проверить:

Запустить backend stack:

```powershell
docker compose up --build
```

Или локально запустить backend с PostgreSQL/Redis, применив миграции:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload
```

Запустить frontend:

```powershell
cd frontend
npm install
npm run dev
```

Открыть:

```text
http://127.0.0.1:5173
```

Проверить:

- Dashboard показывает реальные stats из `/stats`.
- Таблица показывает monitor'ы из `/monitors`.
- Кнопка Check запускает ручную проверку и обновляет статус/latency после ответа backend.
- Кнопка Enable/Disable переключает `is_active`.
- Кнопка Delete удаляет monitor из списка.
- Frontend build проходит:

```powershell
npm run build
```

- Проверено локально: `npm run build` успешно собрал frontend.
- Проверено локально: backend компилируется через `python -m compileall .\app .\alembic`.
- Проверено локально: `app.main` импортируется, FastAPI app содержит `CORSMiddleware`.
- Проверено локально: `CORS_ORIGINS` из environment variable парсится как список origins.
- Проверено локально: Vite dev server отвечает `200` на `http://127.0.0.1:5173`.

Ограничения:

- Для проверки реальных данных нужен запущенный backend и база с примененными миграциями.
- Add Monitor, Details и Incidents pages будут полноценно подключаться к backend на следующих этапах.
- В текущем окружении Docker daemon может быть недоступен; тогда полный `docker compose up --build` нужно повторить после запуска Docker Desktop или Rancher Desktop.

## Этап 15 - Add Monitor page

Что создано:

- Add Monitor page подключена к backend API.
- Форма создания monitor'а стала controlled React form.
- Форма содержит поля `name`, `url`, `interval_seconds`, `expected_status_code`, `timeout_seconds`, `is_active`.
- Добавлена frontend validation для обязательных полей.
- Добавлена validation для `http://` / `https://` URL.
- Добавлена validation для числовых полей: interval и timeout больше `0`, expected status в диапазоне `100..599`.
- Submit формы вызывает `POST /monitors`.
- Добавлены inline success/error messages.
- После успешного создания monitor'а frontend делает redirect на Dashboard.
- Dashboard умеет показать success message, переданный после redirect.

Измененные файлы:

- `README.md`
- `frontend/README.md`
- `frontend/src/pages/AddMonitor.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `PROGRESS.md`

Как проверить:

Запустить backend stack:

```powershell
docker compose up --build
```

Или локально запустить backend с PostgreSQL/Redis, применив миграции:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload
```

Запустить frontend:

```powershell
cd frontend
npm install
npm run dev
```

Открыть:

```text
http://127.0.0.1:5173/monitors/new
```

Проверить:

- Пустые обязательные поля не отправляются.
- Некорректный URL или числовые значения показывают validation error.
- Валидная форма создает monitor через `POST /monitors`.
- После успешного создания происходит redirect на Dashboard.
- Dashboard показывает созданный monitor в таблице.
- Frontend build проходит:

```powershell
npm run build
```

- Проверено локально: `npm run build` успешно собрал frontend.
- Проверено локально: Vite dev server отвечает `200` на `http://127.0.0.1:5173/monitors/new`.

Ограничения:

- Для реального `POST /monitors` нужен запущенный backend и база с примененными миграциями.
- Monitor Details и Incidents pages будут полноценно подключаться к backend на следующих этапах.
- В текущем окружении Docker daemon может быть недоступен; тогда полный `docker compose up --build` нужно повторить после запуска Docker Desktop или Rancher Desktop.

## Этап 16 - Monitor Details page

Что создано:

- Monitor Details page подключена к backend API.
- Страница получает monitor по id через `GET /monitors/{monitor_id}`.
- Страница получает recent checks через `GET /monitors/{monitor_id}/checks`.
- Страница получает incidents через `GET /monitors/{monitor_id}/incidents`.
- Показываются current status, URL, expected status code, interval, timeout и last checked.
- Добавлен uptime percentage на основе recent checks.
- Добавлена кнопка Run Check.
- Run Check вызывает `POST /monitors/{monitor_id}/check`.
- После ручной проверки страница обновляет monitor, recent checks и incidents.
- Recent checks отображаются в таблице.
- Incidents отображаются в таблице.
- Добавлены loading, success и error states.
- Доработаны стили для compact tables, длинных URL и статусов `SUCCESS`, `FAILED`, `OPEN`, `RESOLVED`.

Измененные файлы:

- `README.md`
- `frontend/README.md`
- `frontend/src/pages/MonitorDetails.jsx`
- `frontend/src/styles.css`
- `PROGRESS.md`

Как проверить:

Запустить backend stack:

```powershell
docker compose up --build
```

Или локально запустить backend с PostgreSQL/Redis, применив миграции:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload
```

Запустить frontend:

```powershell
cd frontend
npm install
npm run dev
```

Открыть Dashboard и перейти в details через View:

```text
http://127.0.0.1:5173
```

Проверить:

- Details page показывает monitor configuration.
- Recent checks table показывает историю проверок.
- Incidents table показывает incidents этого monitor'а.
- Кнопка Run Check запускает manual check.
- После manual check обновляется recent checks table и status monitor'а.
- Frontend build проходит:

```powershell
npm run build
```

- Проверено локально: `npm run build` успешно собрал frontend.
- Проверено локально: Vite dev server отвечает `200` на `http://127.0.0.1:5173/monitors/1`.

Ограничения:

- Для реальных monitor/check/incident данных нужен запущенный backend и база с примененными миграциями.
- Incidents list page будет полноценно подключаться к backend на следующем frontend этапе.
- В текущем окружении Docker daemon может быть недоступен; тогда полный `docker compose up --build` нужно повторить после запуска Docker Desktop или Rancher Desktop.

## Этап 17 - Incidents page

Что создано:

- Incidents page подключена к backend API.
- Страница вызывает `GET /incidents`.
- Добавлены фильтры `ALL`, `OPEN`, `RESOLVED`.
- Фильтр `ALL` вызывает `/incidents` без status query.
- Фильтры `OPEN` и `RESOLVED` вызывают `/incidents?status=OPEN` и `/incidents?status=RESOLVED`.
- Таблица показывает Monitor, Status, Started, Resolved, Duration и Reason.
- Monitor в таблице ведет на details page, если backend вернул monitor summary.
- Добавлены loading и error states.
- Доработано поведение длинного текста в таблицах, чтобы reason/URL не ломали layout.

Измененные файлы:

- `README.md`
- `frontend/README.md`
- `frontend/src/pages/Incidents.jsx`
- `frontend/src/styles.css`
- `PROGRESS.md`

Как проверить:

Запустить backend stack:

```powershell
docker compose up --build
```

Или локально запустить backend с PostgreSQL/Redis, применив миграции:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload
```

Запустить frontend:

```powershell
cd frontend
npm install
npm run dev
```

Открыть:

```text
http://127.0.0.1:5173/incidents
```

Проверить:

- Incidents page показывает список incidents из `/incidents`.
- Monitor column ведет на details page monitor'а.
- Фильтр ALL показывает все incidents.
- Фильтр OPEN показывает только open incidents.
- Фильтр RESOLVED показывает только resolved incidents.
- Frontend build проходит:

```powershell
npm run build
```

- Проверено локально: `npm run build` успешно собрал frontend.
- Проверено локально: Vite dev server отвечает `200` на `http://127.0.0.1:5173/incidents`.

Ограничения:

- Для реальных incidents нужен запущенный backend и база с примененными миграциями.
- В текущем окружении Docker daemon может быть недоступен; тогда полный `docker compose up --build` нужно повторить после запуска Docker Desktop или Rancher Desktop.

## Этап 18 - Frontend Docker support

Что создано:

- Создан `frontend/Dockerfile`.
- Dockerfile использует multi-stage build:
  - `node:22-alpine` устанавливает зависимости и собирает React/Vite app;
  - `nginx:1.27-alpine` раздает собранный frontend.
- Создан `frontend/nginx.conf`.
- nginx настроен на SPA fallback через `try_files`.
- nginx проксирует `/api/` в backend service `http://api:8000/`.
- Создан `frontend/.dockerignore`.
- В `docker-compose.yml` добавлен service `frontend`.
- `frontend` собирается из `./frontend`.
- Для Docker build задан `VITE_API_BASE_URL=/api`.
- `frontend` пробрасывает порт `3000:80`.
- `frontend` ждет healthy `api`.
- Для `frontend` добавлен healthcheck через nginx root endpoint.
- Обновлены `README.md` и `frontend/README.md`.

Измененные файлы:

- `README.md`
- `frontend/README.md`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `frontend/.dockerignore`
- `docker-compose.yml`
- `PROGRESS.md`

Как проверить:

Запустить весь stack:

```powershell
docker compose up --build
```

Открыть frontend:

```text
http://localhost:3000
```

Проверить:

- nginx раздает собранный frontend.
- SPA routes вроде `/incidents` и `/monitors/1` открываются напрямую.
- Frontend API calls идут через `/api`.
- nginx проксирует `/api/*` в backend `api:8000`.
- Backend health доступен через frontend proxy:

```text
http://localhost:3000/api/health
```

Локальная проверка без Docker daemon:

```powershell
cd frontend
npm run build
cd ..
docker compose config --quiet
```

- Проверено локально: `npm run build` успешно собрал frontend.
- Проверено локально: `docker compose config --quiet` успешно валидирует Compose файл.
- Проверено локально: `docker compose up --build -d` успешно собрал images и поднял полный stack.
- Проверено локально: `frontend`, `api`, `postgres` и `redis` healthy в `docker compose ps`.
- Проверено локально: `worker` и `scheduler` запущены.
- Проверено локально: `http://localhost:3000` возвращает `200`.
- Проверено локально: SPA route `http://localhost:3000/incidents` возвращает `200`.
- Проверено локально: nginx proxy `http://localhost:3000/api/health` возвращает `{"status":"ok"}`.

Ограничения:

- Docker stack оставлен запущенным после проверки, чтобы frontend можно было открыть на `http://localhost:3000`.

## Этап 19 - Full Docker Compose integration

Что создано:

- `docker-compose.yml` приведен к единой Compose-архитектуре для всех сервисов.
- Compose stack содержит `frontend`, `api`, `postgres`, `redis`, `worker`, `scheduler`.
- Для backend-сервисов добавлены YAML anchors:
  - общий backend image `cloudpulse-backend:local`;
  - общий backend build context;
  - общий набор environment variables.
- `api`, `worker` и `scheduler` используют один backend image.
- `api` подключается к `postgres` через service DNS `postgres:5432`.
- `api`, `worker` и `scheduler` подключаются к Redis через service DNS `redis:6379`.
- `worker` и `scheduler` ждут healthy `api`, `postgres` и `redis`.
- `frontend` ждет healthy `api` и проксирует `/api` в backend через nginx.
- Порты `frontend`, `api`, `postgres`, `redis` вынесены в Compose variables с defaults.
- PostgreSQL credentials и runtime-переменные вынесены в Compose variables с defaults.
- Добавлен root `.env.example` для Docker Compose.
- README дополнен полной инструкцией запуска, проверки статуса, просмотра логов и остановки stack.

Измененные файлы:

- `README.md`
- `.env.example`
- `docker-compose.yml`
- `PROGRESS.md`

Как проверить:

```powershell
copy .env.example .env
docker compose up --build
```

Открыть:

```text
http://localhost:3000
http://localhost:8000/health
http://localhost:3000/api/health
```

Проверить сервисы:

```powershell
docker compose ps
docker compose logs -f scheduler
docker compose logs -f worker
```

Ожидаемый результат:

- `frontend`, `api`, `postgres`, `redis` healthy.
- `worker` и `scheduler` запущены.
- Frontend доступен на `http://localhost:3000`.
- API доступен напрямую на `http://localhost:8000`.
- API доступен через frontend nginx proxy на `http://localhost:3000/api`.
- Можно создать monitor через frontend или API.
- Scheduler добавляет due monitor ids в Redis queue.
- Worker забирает задачи из Redis и создает check results.
- Failed check создает open incident.
- Successful check после восстановления закрывает incident.

Проверено локально:

- `docker compose config --quiet` успешно валидирует Compose файл.
- `docker compose up --build -d` успешно пересобрал images и поднял полный stack.
- `docker compose ps` показывает healthy `frontend`, `api`, `postgres`, `redis`.
- `worker` и `scheduler` находятся в состоянии `Up`.
- `http://localhost:3000` возвращает `200`.
- `http://localhost:3000/api/health` возвращает `{"status":"ok"}`.
- Через proxy создан monitor `Stage19 Scheduler Success`, scheduler поставил задачу, worker выполнил `SUCCESS` check.
- Через proxy создан monitor `Stage19 Incident Flow`, scheduler поставил задачу, worker выполнил `FAILED` check и создал `OPEN` incident.
- После обновления URL monitor'а на healthy endpoint scheduler/worker выполнили `SUCCESS` check и incident перешел в `RESOLVED`.
- Тестовые monitor'ы после проверки переведены в `is_active=false`, чтобы не продолжать фоновые проверки.

Ограничения:

- Docker stack оставлен запущенным после проверки, чтобы frontend можно было открыть на `http://localhost:3000`.

## Этап 20 - Kubernetes manifests for PostgreSQL and Redis

Что создано:

- Создан `k8s/configmap.yaml`.
- Создан `k8s/secret.yaml`.
- Создан `k8s/postgres-deployment.yaml`.
- Создан `k8s/postgres-service.yaml`.
- Создан `k8s/redis-deployment.yaml`.
- Создан `k8s/redis-service.yaml`.
- `cloudpulse-config` хранит обычные настройки: PostgreSQL host/db/user, Redis URL/queue и runtime intervals.
- `cloudpulse-secret` хранит локальный development password для PostgreSQL.
- PostgreSQL Deployment использует image `postgres:16-alpine`.
- PostgreSQL получает настройки из ConfigMap и Secret.
- PostgreSQL использует PVC `postgres-data` на `1Gi`.
- PostgreSQL имеет readiness/liveness probes через `pg_isready`.
- PostgreSQL Service имеет type `ClusterIP` и имя `postgres`.
- Redis Deployment использует image `redis:7-alpine`.
- Redis имеет readiness/liveness probes через `redis-cli ping`.
- Redis Service имеет type `ClusterIP` и имя `redis`.
- Для PostgreSQL и Redis добавлены resource requests и limits.
- README дополнен Kubernetes-инструкцией для infrastructure manifests.

Измененные файлы:

- `README.md`
- `k8s/configmap.yaml`
- `k8s/secret.yaml`
- `k8s/postgres-deployment.yaml`
- `k8s/postgres-service.yaml`
- `k8s/redis-deployment.yaml`
- `k8s/redis-service.yaml`
- `PROGRESS.md`

Как проверить:

```powershell
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

Ожидаемый результат:

- ConfigMap `cloudpulse-config` создан.
- Secret `cloudpulse-secret` создан.
- PVC `postgres-data` создан.
- Pod PostgreSQL запущен и готов.
- Pod Redis запущен и готов.
- Service `postgres` доступен внутри cluster как `ClusterIP` на port `5432`.
- Service `redis` доступен внутри cluster как `ClusterIP` на port `6379`.

Проверено локально:

- Все YAML files в `k8s/` успешно парсятся через PyYAML.
- `kubectl` установлен: client `v1.34.1`.
- Rancher Desktop context `rancher-desktop` активен.
- `kubectl get nodes` показывает node `desktop-ejtj704` в status `Ready`.
- `kubectl apply -f k8s/` успешно создал ConfigMap, Secret, PostgreSQL PVC/Deployment/Service и Redis Deployment/Service.
- `kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=postgres --timeout=120s` успешно дождался PostgreSQL pod.
- `kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=redis --timeout=120s` успешно дождался Redis pod.
- `kubectl get pods` показывает PostgreSQL и Redis в status `Running` и `READY 1/1`.
- `kubectl get services` показывает `postgres` и `redis` как `ClusterIP`.
- `kubectl get pvc` показывает `postgres-data` в status `Bound`.
- Docker Compose stack из предыдущего этапа остается рабочим: `http://localhost:3000/api/health` возвращает `{"status":"ok"}`.

Ограничения:

- `k8s/secret.yaml` содержит local development password; перед использованием вне локальной среды его нужно заменить.

## Этап 21 - Kubernetes manifests for API, worker and scheduler

Что создано:

- Создан `k8s/api-deployment.yaml`.
- Создан `k8s/api-service.yaml`.
- Создан `k8s/worker-deployment.yaml`.
- Создан `k8s/scheduler-deployment.yaml`.
- API Deployment использует image `cloudpulse-backend:local`.
- API container слушает port `8000`.
- API перед стартом выполняет `alembic upgrade head`.
- API запускает `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- API получает environment variables из `cloudpulse-config` и `cloudpulse-secret`.
- `DATABASE_URL` собирается через Kubernetes env expansion из PostgreSQL user/password/db.
- API получил readiness/liveness probes через `GET /health`.
- `api-service` имеет type `ClusterIP` и port `8000`.
- Worker Deployment использует тот же backend image и command `python -m app.worker`.
- Scheduler Deployment использует тот же backend image и command `python -m app.scheduler`.
- Worker и scheduler получают environment variables из ConfigMap и Secret.
- Worker и scheduler используют initContainer `wait-for-api`, чтобы стартовать после доступности `api-service`.
- Для API, worker и scheduler добавлены resource requests и limits.
- README дополнен Kubernetes backend инструкциями и подсказкой по загрузке local image в Rancher Desktop containerd.

Измененные файлы:

- `README.md`
- `k8s/api-deployment.yaml`
- `k8s/api-service.yaml`
- `k8s/worker-deployment.yaml`
- `k8s/scheduler-deployment.yaml`
- `PROGRESS.md`

Как проверить:

```powershell
kubectl apply -f k8s/
kubectl get pods
kubectl logs deployment/api
kubectl logs deployment/worker
kubectl logs deployment/scheduler
kubectl port-forward service/api-service 8000:8000
```

Открыть:

```text
http://localhost:8000/health
```

Ожидаемый результат:

- Pods `api`, `worker`, `scheduler`, `postgres`, `redis` находятся в status `Running`.
- Deployment `api`, `worker`, `scheduler` доступны.
- API применяет Alembic migration и отвечает `{"status":"ok"}` на `/health`.
- Worker подключается к Redis queue.
- Scheduler подключается к PostgreSQL и Redis queue.
- Scheduler добавляет due monitor ids в Redis.
- Worker забирает monitor ids и создает check results.

Проверено локально:

- Все YAML files в `k8s/` успешно парсятся через PyYAML.
- Local image `cloudpulse-backend:local` загружен в Rancher Desktop containerd namespace `k8s.io`.
- `kubectl apply -f k8s/` успешно создал API, worker и scheduler resources.
- `kubectl wait --for=condition=available deployment/api --timeout=180s` успешно дождался API.
- `kubectl wait --for=condition=available deployment/worker --timeout=180s` успешно дождался worker.
- `kubectl wait --for=condition=available deployment/scheduler --timeout=180s` успешно дождался scheduler.
- `kubectl get pods` показывает `api`, `worker`, `scheduler`, `postgres`, `redis` в status `Running` и `READY 1/1`.
- `kubectl logs deployment/api` показывает Alembic migration и Uvicorn startup.
- `kubectl logs deployment/worker` показывает запуск worker с Redis queue `monitor_checks`.
- `kubectl logs deployment/scheduler` показывает запуск scheduler и scheduler cycles.
- Через `kubectl port-forward service/api-service 18000:8000` endpoint `/health` вернул `{"status":"ok"}`.
- Через port-forward создан тестовый monitor `Stage21 K8s Scheduler Success`.
- Scheduler поставил задачу для monitor id `1`.
- Worker выполнил check со status `SUCCESS`.
- Тестовый monitor после проверки переведен в `is_active=false`.

Ограничения:

- Для проверки на `localhost:8000` нужно освободить port `8000` или остановить Docker Compose API; во время проверки использовался `18000:8000`, потому что Compose stack уже занимал `8000`.

## Этап 22 - Kubernetes manifests for frontend

Что создано:

- Создан `k8s/frontend-deployment.yaml`.
- Создан `k8s/frontend-service.yaml`.
- Frontend Deployment использует image `cloudpulse-frontend:local`.
- Добавлен ConfigMap `frontend-nginx-config` с nginx config для Kubernetes.
- nginx раздает React/Vite build и поддерживает SPA routes через `try_files`.
- nginx проксирует `/api/*` во внутренний Kubernetes service `api-service:8000`.
- Frontend container слушает port `80`.
- Добавлены readiness/liveness probes через `GET /`.
- `frontend-service` имеет type `ClusterIP` и port `80`.
- README дополнен Kubernetes frontend инструкциями, загрузкой local frontend image в Rancher Desktop containerd и port-forward командами.

Измененные файлы:

- `README.md`
- `k8s/frontend-deployment.yaml`
- `k8s/frontend-service.yaml`
- `PROGRESS.md`

Как проверить:

```powershell
kubectl apply -f k8s/
kubectl get pods
kubectl get services
kubectl port-forward service/frontend-service 3000:80
```

Открыть:

```text
http://localhost:3000
http://localhost:3000/api/health
```

Ожидаемый результат:

- Pods `frontend`, `api`, `worker`, `scheduler`, `postgres`, `redis` находятся в status `Running`.
- Service `frontend-service` доступен внутри cluster как `ClusterIP` на port `80`.
- Frontend доступен через port-forward.
- SPA routes вроде `/incidents` открываются напрямую.
- API доступен через frontend nginx proxy на `/api`.

Проверено локально:

- Все YAML files в `k8s/` успешно парсятся через PyYAML.
- Local image `cloudpulse-frontend:local` загружен в Rancher Desktop containerd namespace `k8s.io`.
- `kubectl apply -f k8s/` успешно создал ConfigMap `frontend-nginx-config`, Deployment `frontend` и Service `frontend-service`.
- `kubectl wait --for=condition=available deployment/frontend --timeout=180s` успешно дождался frontend.
- `kubectl get pods` показывает `frontend`, `api`, `worker`, `scheduler`, `postgres`, `redis` в status `Running` и `READY 1/1`.
- `kubectl get services` показывает `frontend-service` как `ClusterIP` на port `80`.
- Через `kubectl port-forward service/frontend-service 13000:80` endpoint `/` вернул `200` и frontend HTML.
- Через тот же port-forward SPA route `/incidents` вернул `200` и frontend HTML.
- Через тот же port-forward endpoint `/api/health` вернул `{"status":"ok"}` через nginx proxy на `api-service`.

Ограничения:

- Для проверки на `localhost:3000` нужно освободить port `3000` или остановить Docker Compose frontend; во время проверки использовался `13000:80`, потому что Compose stack уже занимал `3000`.

## Этап 23 - GitHub Actions CI workflow

Что создано:

- Создан workflow `.github/workflows/ci.yml`.
- Workflow запускается на `push` и `pull_request`.
- Добавлен job `backend`.
- Backend job устанавливает Python `3.13`.
- Backend job устанавливает зависимости из `backend/requirements.txt`.
- Backend job проверяет импорт FastAPI приложения через `from app.main import app`.
- Backend job запускает `pytest`, если в backend есть test files.
- Добавлен job `frontend`.
- Frontend job устанавливает Node.js `22`.
- Frontend job выполняет `npm ci`.
- Frontend job выполняет `npm run build`.
- Добавлен job `docker`.
- Docker job собирает image `cloudpulse-backend:ci` из `./backend`.
- Docker job собирает image `cloudpulse-frontend:ci` из `./frontend`.
- README дополнен разделом CI.

Измененные файлы:

- `.github/workflows/ci.yml`
- `README.md`
- `PROGRESS.md`

Как проверить:

```powershell
git push
```

После push или pull request открыть GitHub Actions и проверить workflow `CI`.

Локальные аналоги проверки:

```powershell
cd backend
.\.venv\Scripts\python -c "from app.main import app; print(app.title)"

cd ..\frontend
npm run build

cd ..
docker build -t cloudpulse-backend:ci .\backend
docker build --build-arg VITE_API_BASE_URL=/api -t cloudpulse-frontend:ci .\frontend
```

Ожидаемый результат:

- Backend dependencies устанавливаются без ошибок.
- Backend приложение импортируется без ошибок.
- Если backend tests есть, они запускаются через `pytest`.
- Frontend dependencies устанавливаются через `npm ci`.
- Frontend production build проходит успешно.
- Docker images для backend и frontend собираются успешно.

Проверено локально:

- `.github/workflows/ci.yml` успешно парсится как YAML.
- Backend import check вернул `CloudPulse API`.
- В backend пока нет test files, поэтому pytest step в CI будет пропущен.
- `npm run build` успешно собрал frontend.
- `docker build --no-cache -t cloudpulse-backend:ci ./backend` успешно собрал backend image.
- `docker build --no-cache --build-arg VITE_API_BASE_URL=/api -t cloudpulse-frontend:ci ./frontend` успешно собрал frontend image, включая `npm ci` и `npm run build` внутри контейнера.
- Docker images `cloudpulse-backend:ci` и `cloudpulse-frontend:ci` присутствуют локально.

Ограничения:

- Полная проверка GitHub Actions возможна после push в GitHub.
- Локальный `npm ci` на Windows был заблокирован активным Vite dev server на port `5173`, который держал `esbuild.exe`; это не влияет на CI, потому что workflow запускается в чистой Linux-среде.

## Этап 24 - Optional cloud deployment workflow

Что создано:

- Создан workflow `.github/workflows/deploy.yml`.
- Workflow запускается вручную через `workflow_dispatch`.
- Workflow подготовлен для Google Cloud Run deployment.
- Добавлена аутентификация в Google Cloud через Workload Identity Federation.
- Добавлен `gcloud` setup через `google-github-actions/setup-gcloud@v2`.
- Добавлена настройка Docker auth для Google Artifact Registry.
- Backend image собирается из `./backend`.
- Frontend image собирается из `./frontend`.
- Frontend image получает `VITE_API_BASE_URL` из GitHub Actions variable `FRONTEND_API_BASE_URL`.
- Backend и frontend images пушатся в Artifact Registry с тегами commit SHA и `latest`.
- Backend deploy step использует Cloud Run service `CLOUD_RUN_BACKEND_SERVICE`.
- Frontend deploy step использует Cloud Run service `CLOUD_RUN_FRONTEND_SERVICE`.
- Backend Cloud Run service получает runtime env vars `DATABASE_URL`, `REDIS_URL`, `REDIS_QUEUE_NAME`, `CORS_ORIGINS`, `ENVIRONMENT`.
- Добавлен validation step, который останавливает workflow с понятной ошибкой, если required secrets или variables не настроены.
- README дополнен разделом Cloud Deployment и списком required secrets/variables.

Измененные файлы:

- `.github/workflows/deploy.yml`
- `README.md`
- `PROGRESS.md`

Как проверить:

- Открыть GitHub Actions после push и убедиться, что workflow `Deploy to Google Cloud` виден.
- Настроить required GitHub Secrets:
  - `GCP_WORKLOAD_IDENTITY_PROVIDER`
  - `GCP_SERVICE_ACCOUNT`
  - `CLOUD_RUN_DATABASE_URL`
  - `CLOUD_RUN_REDIS_URL`
- Настроить required GitHub Variables:
  - `GCP_PROJECT_ID`
  - `GAR_LOCATION`
  - `GAR_REPOSITORY`
  - `CLOUD_RUN_REGION`
  - `CLOUD_RUN_BACKEND_SERVICE`
  - `CLOUD_RUN_FRONTEND_SERVICE`
  - `FRONTEND_API_BASE_URL`
  - `CLOUD_RUN_CORS_ORIGINS`
- Запустить workflow вручную через GitHub Actions.

Ожидаемый результат:

- Workflow аутентифицируется в Google Cloud без hardcoded credentials.
- Docker images собираются и пушатся в Artifact Registry.
- Backend и frontend деплоятся в Cloud Run.
- В workflow logs выводятся backend и frontend Cloud Run URLs.

Проверено локально:

- `.github/workflows/deploy.yml` успешно парсится как YAML.
- Workflow содержит job `cloud-run`.
- В workflow не захардкожены Google Cloud credentials.
- Docker build для backend уже проверен на этапе 23 через `docker build --no-cache -t cloudpulse-backend:ci ./backend`.
- Docker build для frontend уже проверен на этапе 23 через `docker build --no-cache --build-arg VITE_API_BASE_URL=/api -t cloudpulse-frontend:ci ./frontend`.

Ограничения:

- Реальный deploy не запускался локально, потому что для него нужны Google Cloud project, Artifact Registry repository, Cloud Run permissions и GitHub Secrets.
- Workflow покрывает frontend/API deployment; worker, scheduler, managed PostgreSQL и Redis-compatible сервис должны быть подготовлены отдельно для production.
- Для cross-origin frontend/backend схемы нужно задать `CLOUD_RUN_CORS_ORIGINS` в формате JSON list, например `["https://frontend-service-url"]`.

## Этап 25 - Backend tests

Что создано:

- Добавлен `pytest` в `backend/requirements.txt`.
- Создан каталог `backend/tests/`.
- Создан `backend/tests/conftest.py` с общими pytest fixtures.
- Тесты используют FastAPI `TestClient`.
- Для API tests настроена in-memory SQLite database через SQLAlchemy `StaticPool`.
- Dependency `get_db` подменяется на тестовую database session.
- Создан `backend/tests/test_api.py`.
- Добавлен test для `GET /health`.
- Добавлен test для создания monitor через `POST /monitors`.
- Добавлен test для validation ошибки при invalid monitor URL.
- Добавлен test для получения списка monitors через `GET /monitors`.
- Создан `backend/tests/test_checker.py`.
- Добавлен mocked HTTP client для checker service.
- Добавлен test успешной проверки monitor'а: создается `CheckResult`, monitor переходит в `UP`.
- Добавлен test failed HTTP status: создается `FAILED` check result, monitor переходит в `DOWN`, открывается incident.
- README и `backend/README.md` дополнены командами запуска tests.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `backend/requirements.txt`
- `backend/tests/conftest.py`
- `backend/tests/test_api.py`
- `backend/tests/test_checker.py`
- `PROGRESS.md`

Как проверить:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

Ожидаемый результат:

- Все backend tests проходят.
- Для tests не нужны запущенные PostgreSQL, Redis или Docker Compose.
- Checker tests не выполняют реальные HTTP requests.

Проверено локально:

- `python -m pip install -r requirements.txt` успешно установил `pytest==8.3.5`.
- `python -m pytest -q` завершился успешно.
- Результат: `6 passed`.
- GitHub Actions YAML files по-прежнему успешно парсятся.

Ограничения:

- Tests пока покрывают базовые API и checker behavior, но не покрывают Redis queue, worker, scheduler, stats и все incident edge cases.
- Test database использует SQLite, поэтому PostgreSQL-specific поведение дополнительно проверяется через Docker Compose/Kubernetes flows.
- Повторная локальная Docker build проверка backend после изменения `requirements.txt` не завершилась из-за локальной проблемы Docker BuildKit/buildx: `docker buildx ls` показывает builder status `error` и `DeadlineExceeded`.

## Этап 26 - Final README and project polish

Что создано:

- Root `README.md` переписан как финальный проектный документ.
- README теперь содержит project description.
- README содержит architecture overview и text architecture diagram.
- README содержит services list.
- README содержит main features.
- README содержит local Docker Compose run instructions.
- README содержит local backend/frontend run instructions.
- README содержит Kubernetes run instructions for Rancher Desktop.
- README содержит список Kubernetes objects.
- README содержит API endpoints table.
- README содержит backend tests instructions.
- README содержит CI/CD description.
- README содержит Google Cloud Run deployment secrets/variables.
- README содержит screenshots placeholders.
- README содержит security/secrets notes.
- README содержит known limitations.
- README содержит troubleshooting notes.
- README содержит future improvements.
- Создан `docs/screenshots/README.md` с именами ожидаемых demo screenshots.
- `backend/README.md` обновлен: устаревший stage status заменен актуальным описанием backend.
- `frontend/README.md` обновлен: устаревший stage status заменен актуальным описанием frontend.

Измененные файлы:

- `README.md`
- `backend/README.md`
- `frontend/README.md`
- `docs/screenshots/README.md`
- `PROGRESS.md`

Как проверить:

```powershell
cd backend
.\.venv\Scripts\python -m pytest -q

cd ..\frontend
npm run build

cd ..
docker compose config --quiet
kubectl apply -f k8s/
```

Ожидаемый результат:

- README понятно объясняет проект и основные сценарии запуска.
- PROGRESS содержит записи по всем этапам.
- Backend tests проходят.
- Frontend production build проходит.
- Docker Compose config валиден.
- Kubernetes YAML files валидны и применяются в готовом Rancher Desktop cluster.
- Production secrets не хранятся в репозитории.

Проверено локально:

- `python -m pytest -q` в `backend/` завершился успешно: `6 passed`.
- `npm run build` в `frontend/` завершился успешно.
- GitHub Actions workflow YAML files успешно парсятся.
- Kubernetes YAML files успешно парсятся.
- `docker compose config --quiet` завершился успешно.
- `http://localhost:8000/health` вернул `{"status":"ok"}`.
- `http://localhost:3000` вернул frontend HTML.
- `http://localhost:3000/api/health` вернул `{"status":"ok"}`.
- `http://localhost:8000/stats` вернул dashboard stats.
- Secret pattern scan по workflows/docs не нашел private keys, cloud tokens, GitHub tokens или client secrets.
- `PROGRESS.md` содержит записи для этапов 0-26.

Ограничения:

- `kubectl get pods --request-timeout=10s` сейчас не подключился к локальному Rancher Desktop API: `Client.Timeout exceeded while awaiting headers`; ранее Kubernetes stack был успешно применен и проверен на этапах 20-22.
- `docker buildx ls` сейчас показывает Docker builder status `error` и `DeadlineExceeded`; поэтому повторная Docker image build проверка в этом этапе не выполнялась.
- В репозитории есть local development defaults: `.env.example` и `k8s/secret.yaml` используют пароль `cloudpulse`; README явно отмечает, что это не production secret и должно заменяться вне локальной среды.
