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

заполнить бд (по умолчанию 100 строк)

    docker exec -it ucar-app python -m app.utils.generate_incidents

запустить нагрузочное тестирование

    docker-compose --profile load-test up load-test

удалить контейнеры

    docker-compose down -v
    docker-compose --profile load-test down


psycopg[binary] — использует бинарные расширения (быстрее)
psycopg[pool] — включает встроенный пул соединений (но SQLAlchemy использует свой, так что это опционально)
sqlalchemy[asyncio]

asyncpg alembic granian itsdangerous pydantic-settings pylint requests ruff sqlalchemy structlog "fastapi[standard]"


granian[uvloop]  Requests/sec:   3203.57
granian          Requests/sec:   2919.04
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


ssh -A -i ~/.ssh/yandex_cloud_20250211 ubuntu@84.201.133.152
docker compose --profile load-test up load-test

FastAPI оптимизации:

    Используйте uvicorn с несколькими воркерами
    Включайте response_model для валидации
    Применяйте FastAPI Cache
    Используйте connection pooling

результаты тестов
в бд 100 записей. /v1/incident отдаёт все 100
```text
psycopg c pool_recycle=300
load-test  | Running 10m test @ http://ucar-app:8000/v1/incident
load-test  |   6 threads and 78 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency   114.34ms   52.13ms 392.37ms   62.69%
load-test  |     Req/Sec   114.24     30.75   252.00     69.68%
load-test  |   Latency Distribution
load-test  |      50%  120.65ms
load-test  |      75%  153.73ms
load-test  |      90%  178.28ms
load-test  |      99%  219.70ms
load-test  |   409806 requests in 10.00m, 7.11GB read
load-test  | Requests/sec:    682.92
load-test  | Transfer/sec:     12.13MB
load-test exited with code 0
```
```text
psycopg без pool_recycle=300
load-test  | Running 10m test @ http://ucar-app:8000/v1/incident
load-test  |   6 threads and 78 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency   115.86ms   71.15ms   1.08s    57.17%
load-test  |     Req/Sec   114.32     32.62   232.00     62.88%
load-test  |   Latency Distribution
load-test  |      50%  104.82ms
load-test  |      75%  182.10ms
load-test  |      90%  208.67ms
load-test  |      99%  282.48ms
load-test  |   410164 requests in 10.00m, 7.12GB read
load-test  | Requests/sec:    683.56
load-test  | Transfer/sec:     12.14MB
load-test exited with code 0
```
```text
asyncpg без pool_recycle=300
load-test  | Running 10m test @ http://ucar-app:8000/v1/incident
load-test  |   6 threads and 78 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency   109.16ms   54.53ms 814.95ms   61.47%
load-test  |     Req/Sec   120.06     28.30   222.00     61.84%
load-test  |   Latency Distribution
load-test  |      50%  108.61ms
load-test  |      75%  152.30ms
load-test  |      90%  181.08ms
load-test  |      99%  226.09ms
load-test  |   430550 requests in 10.00m, 7.47GB read
load-test  | Requests/sec:    717.49
load-test  | Transfer/sec:     12.75MB
load-test exited with code 0
```

