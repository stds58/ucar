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

ендпоинты бенчмарка

    GET /v1/incident/orm
    GET /v1/incident/raw_sql
    GET /v1/incident/native
    GET /v1/incident/dummy
    GET /v1/incident/router-dummy
    GET /v1/incident/native/cache

заполнить бд (по умолчанию 100 строк)

    docker exec -it ucar-app python -m app.utils.generate_incidents

доступ через боаузер

    http://127.0.0.1:8000/api/docs


запустить нагрузочное тестирование

    docker-compose --profile load-test up load-test

удалить контейнеры

    docker-compose down -v
    docker-compose --profile load-test down

## бенчмарки

ендпоинты бенчмарка

параметры системы общие для всех тестов:
- конфиг для посгреса
- пг боунсер
- 6 воркеров граниана
- процессор 12th Gen Intel(R) Core(TM) i5-12400   2.50 GHz
- озу 16,0 ГБ
- 64-разрядная винда
- докер

параметры теста:
- wrk
- в бд 100 строк
- получаем все 100 строк. в глупых запросах - 100 слоаврей
- 6 воркеров
- 96 потоков в воркере
- длительность 60 секунд
- смотрим задержки и рпс

если тест делать 10 минут, результаты скромнее

**сравнительная таблица**

```text
тест         | rps
router-dummy | 8252.46
dummy        | 8144.47
orm          |  966.88
raw_sql      | 1125.60
native       | 1938.89
native+cache | 2138.67
```

**/v1/incident/router-dummy**
- ручка фастапи выводит 100 словарей. 
- используется только апи слой.
```text
load-test  | Running 1m test @ http://ucar-app:8000/v1/incident/router-dummy
load-test  |   6 threads and 96 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency    12.13ms    8.26ms  60.52ms   60.56%                                                                                                                                                                     
load-test  |     Req/Sec     1.38k   510.72     2.89k    76.33%                                                                                                                                                                     
load-test  |   Latency Distribution                                                                                                                                                                                                 
load-test  |      50%   11.41ms                                                                                                                                                                                                     
load-test  |      75%   17.60ms                                                                                                                                                                                                     
load-test  |      90%   23.95ms
load-test  |      99%   31.83ms                                                                                                                                                                                                     
load-test  |   495752 requests in 1.00m, 1.16GB read                                                                                                                                                                                
load-test  |   Socket errors: connect 0, read 0, write 0, timeout 2                                                                                                                                                                 
load-test  | Requests/sec:   8252.46                                                                                                                                                                                                
load-test  | Transfer/sec:     19.82MB     
```

**/v1/incident/dummy**
- метод в круд слое выводит 100 словарей. посгрес не используется
- смотрим сколько ресурсов тратится на посгрес
```text
load-test  | Running 1m test @ http://ucar-app:8000/v1/incident/dummy
load-test  |   6 threads and 96 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency    11.93ms    7.50ms  53.24ms   56.87%                                                                                                                                                                     
load-test  |     Req/Sec     1.36k   358.34     2.32k    64.41%                                                                                                                                                                     
load-test  |   Latency Distribution                                                                                                                                                                                                 
load-test  |      50%   11.91ms                                                                                                                                                                                                     
load-test  |      75%   18.15ms
load-test  |      90%   22.97ms                                                                                                                                                                                                     
load-test  |      99%   26.12ms                                                                                                                                                                                                     
load-test  |   489368 requests in 1.00m, 1.15GB read                                                                                                                                                                                
load-test  | Requests/sec:   8144.47                                                                                                                                                                                                
load-test  | Transfer/sec:     19.56MB   
```

**/v1/incident/orm**
- используем alchemy orm
```text
load-test  | Running 1m test @ http://ucar-app:8000/v1/incident/orm
load-test  |   6 threads and 96 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency    96.22ms   52.67ms   1.13s    86.41%                                                                                                                                                                     
load-test  |     Req/Sec   172.14     37.06   270.00     68.94%                                                                                                                                                                     
load-test  |   Latency Distribution                                                                                                                                                                                                 
load-test  |      50%   78.21ms                                                                                                                                                                                                     
load-test  |      75%   95.88ms                                                                                                                                                                                                     
load-test  |      90%  156.21ms                                                                                                                                                                                                     
load-test  |      99%  293.90ms                                                                                                                                                                                                     
load-test  |   58052 requests in 1.00m, 1.01GB read                                                                                                                                                                                 
load-test  |   Socket errors: connect 0, read 0, write 0, timeout 96                                                                                                                                                                
load-test  | Requests/sec:    966.88                                                                                                                                                                                                
load-test  | Transfer/sec:     17.18MB     
```

**/v1/incident/raw_sql**
- используем alchemy core и asyncio.get_running_loop
```text
load-test  | Running 1m test @ http://ucar-app:8000/v1/incident/raw_sql
load-test  |   6 threads and 96 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency    97.33ms   86.68ms 917.25ms   87.78%                                                                                                                                                                     
load-test  |     Req/Sec   189.57     43.03   340.00     71.32%                                                                                                                                                                     
load-test  |   Latency Distribution                                                                                                                                                                                                 
load-test  |      50%   53.12ms                                                                                                                                                                                                     
load-test  |      75%  150.85ms                                                                                                                                                                                                     
load-test  |      90%  213.32ms                                                                                                                                                                                                     
load-test  |      99%  378.62ms                                                                                                                                                                                                     
load-test  |   67641 requests in 1.00m, 1.17GB read                                                                                                                                                                                 
load-test  | Requests/sec:   1125.60                                                                                                                                                                                                
load-test  | Transfer/sec:     20.00MB   
```

**/v1/incident/native**
- используем get_asyncpg_pool
```text
load-test  | Running 1m test @ http://ucar-app:8000/v1/incident/native
load-test  |   6 threads and 96 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency    48.95ms   29.87ms   1.47s    89.76%                                                                                                                                                                     
load-test  |     Req/Sec   336.26     73.63   580.00     75.71%                                                                                                                                                                     
load-test  |   Latency Distribution                                                                                                                                                                                                 
load-test  |      50%   46.53ms                                                                                                                                                                                                     
load-test  |      75%   58.15ms                                                                                                                                                                                                     
load-test  |      90%   72.12ms                                                                                                                                                                                                     
load-test  |      99%  126.13ms                                                                                                                                                                                                     
load-test  |   116418 requests in 1.00m, 2.13GB read                                                                                                                                                                                
load-test  |   Socket errors: connect 0, read 0, write 0, timeout 94
load-test  | Requests/sec:   1938.89                                                                                                                                                                                                
load-test  | Transfer/sec:     36.30MB       
```

**/v1/incident/native/cache**
- типа кеш с get_asyncpg_pool
```text
load-test  | Running 1m test @ http://ucar-app:8000/v1/incident/native/cache
load-test  |   6 threads and 96 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency    45.61ms   26.50ms 417.20ms   72.44%                                                                                                                                                                     
load-test  |     Req/Sec   358.93    105.45   686.00     70.04%                                                                                                                                                                     
load-test  |   Latency Distribution                                                                                                                                                                                                 
load-test  |      50%   45.32ms                                                                                                                                                                                                     
load-test  |      75%   62.24ms                                                                                                                                                                                                     
load-test  |      90%   78.06ms                                                                                                                                                                                                     
load-test  |      99%  105.94ms                                                                                                                                                                                                     
load-test  |   128488 requests in 1.00m, 2.35GB read                                                                                                                                                                                
load-test  | Requests/sec:   2138.67                                                                                                                                                                                                
load-test  | Transfer/sec:     40.04MB 
```


**pg bounser**

    docker exec ucar-pgbouncer cat /opt/bitnami/pgbouncer/conf/pgbouncer.ini

- pool_mode


    В транзакционном режиме (pool_mode = transaction) PgBouncer не поддерживает PREPARE и PREPARED STATEMENTS

- PGBOUNCER_DEFAULT_POOL_SIZE = 25


    Это максимальное число одновременных (активных) соединений от PgBouncer к одной базе данных на один пользователь.
    В вашем случае у вас одна БД (ucar_db) и один пользователь (admin), значит этот пул — глобальный для всех клиентов.
    То есть PgBouncer не будет открывать больше 25 соединений к PostgreSQL одновременно для текущих транзакций.

- PGBOUNCER_RESERVE_POOL_SIZE = 5


    Это дополнительные соединения, которые PgBouncer может использовать в пиковые моменты, когда основной пул исчерпан.
    Итого: максимум активных соединений = 25 + 5 = 30.

    ⚠️ Но! Это не максимальное количество соединений вообще, а максимум одновременно используемых соединений к БД.
 
- DEFAULT_POOL_SIZE + RESERVE_POOL_SIZE
	

    Одновременно активные соединения (те, что реально используются прямо сейчас).

- MAX_DB_CONNECTIONS
	

    Общее количество соединений, которые PgBouncer может открыть к PostgreSQL-e
    за всё время своей работы (включая простаивающие в пуле).

**библиотеки**

asyncpg alembic granian[uvloop] itsdangerous sqlalchemy[asyncio] "fastapi[standard]"

- asyncpg — Асинхронный драйвер для PostgreSQL
- asyncio — Встроенная библиотека Python для асинхронности
- psycopg[binary,pool] — использует бинарные расширения (быстрее)
- psycopg[pool] — включает встроенный пул соединений (но SQLAlchemy использует свой, так что это опционально)
- sqlalchemy[asyncio]
- FastAPI — Веб-фреймворк, работает асинхронно (async def , await) 
- granian[uvloop] — ASGI сервер (как uvicorn , hypercorn)
```text
granian[uvloop]  Requests/sec:   3203.57
granian          Requests/sec:   2919.04
```

**wrk**

```text
command: ["-t", "2", "-c", "78", "-d", "20s", "--latency", "http://ucar-app:8000/v1/incident"]
Флаг	Значение
`-t 2`	**Количество потоков** (`threads`) — `wrk` использует **2 потока** для отправки запросов.
`-c 78`	**Количество соединений** (`connections`) — `wrk` держит **78 HTTP-соединений** открытыми и посылает запросы по ним.
`-d 20s`	**Длительность теста** (`duration`) — тест будет работать **20 секунд**.
`--latency`	**Включить измерение латентности** — `wrk` будет **считать и показывать статистику задержек** (например, 50%, 90%, 99% перцентили).
`http://ucar-app:8000/v1/incident`	**URL**, который тестируется.
```

**логирование**
https://habr.com/ru/articles/575454/


**FastAPI оптимизации**

- Используйте uvicorn с несколькими воркерами
- Включайте response_model для валидации
- Применяйте FastAPI Cache
- Используйте connection pooling

**результаты 10 минутных тестов с разными настройками**

- в бд 100 записей. /v1/incident отдаёт все 100

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

```text
load-test  | Running 10m test @ http://ucar-app:8000/v1/incident
load-test  |   6 threads and 78 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency    82.79ms   28.31ms   1.24s    77.61%                                                                                                                                                                     
load-test  |     Req/Sec   158.39     29.56   262.00     69.70%                                                                                                                                                                     
load-test  |   Latency Distribution                                                                                                                                                                                                 
load-test  |      50%   76.59ms                                                                                                                                                                                                     
load-test  |      75%   94.79ms                                                                                                                                                                                                     
load-test  |      90%  117.84ms                                                                                                                                                                                                     
load-test  |      99%  168.24ms                                                                                                                                                                                                     
load-test  |   564350 requests in 10.00m, 9.79GB read                                                                                                                                                                               
load-test  |   Socket errors: connect 0, read 0, write 0, timeout 78                                                                                                                                                                
load-test  | Requests/sec:    940.50                                                                                                                                                                                                
load-test  | Transfer/sec:     16.71MB                                                                                                                                                                                              
load-test exited with code 0
```

```text
с asyncio
load-test  | Running 10m test @ http://ucar-app:8000/v1/incident
load-test  |   6 threads and 78 connections
load-test  |   Thread Stats   Avg      Stdev     Max   +/- Stdev
load-test  |     Latency    54.82ms   24.14ms 707.01ms   68.69%                                                                                                                                                                     
load-test  |     Req/Sec   239.66     48.81   410.00     68.68%                                                                                                                                                                     
load-test  |   Latency Distribution                                                                                                                                                                                                 
load-test  |      50%   52.55ms                                                                                                                                                                                                     
load-test  |      75%   70.37ms                                                                                                                                                                                                     
load-test  |      90%   84.45ms                                                                                                                                                                                                     
load-test  |      99%  106.29ms                                                                                                                                                                                                     
load-test  |   858480 requests in 10.00m, 15.69GB read                                                                                                                                                                              
load-test  | Requests/sec:   1430.62
load-test  | Transfer/sec:     26.78MB                                                                                                                                                                                              
load-test exited with code 0

```

