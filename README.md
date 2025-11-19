## Развёртывание

клонируйте репозиторий
https://github.com/stds58/ucar.git

создайте .env из .env.example со своими значениями

создайте docker контейнер с БД и запустите его

    docker-compose up --build

подождите несколько минут когда контейнеры запустятся<br>

[сваггер](http://127.0.0.1:8000/api/docs)

ендпоинты

    GET /v1/incident
    POST /v1/incident
    PATCH /v1/incident/{incident_id}

запустить нагрузочное тестирование

    docker-compose --profile load-test up load-test

удалить контейнеры

    docker-compose down -v
    docker-compose --profile load-test down


asyncpg alembic granian itsdangerous pydantic-settings pylint requests ruff sqlalchemy structlog "fastapi[standard]"


granian[uvloop]
psycopg[binary,pool]

granian | ASGI сервер (как uvicorn , hypercorn)
asyncio | Встроенная библиотека Python для асинхронности
FastAPI | Веб-фреймворк, работает асинхронно (async def , await) 
asyncpg | Асинхронный драйвер для PostgreSQL


command: ["-t", "2", "-c", "78", "-d", "20s", "--latency", "http://ucar-app:8000/v1/incident"]
Флаг	Значение
`-t 2`	**Количество потоков** (`threads`) — `wrk` использует **2 потока** для отправки запросов.
`-c 78`	**Количество соединений** (`connections`) — `wrk` держит **78 HTTP-соединений** открытыми и посылает запросы по ним.
`-d 20s`	**Длительность теста** (`duration`) — тест будет работать **20 секунд**.
`--latency`	**Включить измерение латентности** — `wrk` будет **считать и показывать статистику задержек** (например, 50%, 90%, 99% перцентили).
`http://ucar-app:8000/v1/incident`	**URL**, который тестируется.


логирование
https://habr.com/ru/articles/575454/


