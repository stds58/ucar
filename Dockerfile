FROM python:3.13-slim AS builder

ARG WORKDIR=/opt/backend

WORKDIR $WORKDIR
RUN pip install uv
ENV PATH="$WORKDIR/.venv/bin:$PATH"

COPY pyproject.toml .
RUN uv sync


FROM python:3.13-slim

ARG WORKDIR=/opt/backend
ARG USER=appuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR $WORKDIR

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder $WORKDIR/.venv $WORKDIR/.venv
ENV PATH="$WORKDIR/.venv/bin:$PATH"

RUN useradd -m appuser

COPY . .

ENV PATH="$WORKDIR/.venv/bin:$PATH"
USER appuser

ENTRYPOINT ["/bin/sh", "-c", "alembic upgrade head && exec \"$@\"", "migrate-and-run"]
CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "--workers", "6", "--no-access-log", "app.main:app"]