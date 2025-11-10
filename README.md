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
