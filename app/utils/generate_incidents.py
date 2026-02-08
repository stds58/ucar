"""
docker exec -it ucar-app python app/utils/generate_incidents.py
docker exec -it ucar-app env PYTHONPATH=/opt/backend python /opt/backend/app/utils/generate_incidents.py
docker exec -it ucar-app python -m app.utils.generate_incidents
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH (если запускаете извне)
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import create_session_factory
from app.models.incident import Incident
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


async def generate_fake_incidents(
    session: AsyncSession,
    count: int = 100_000,
    batch_size: int = 1000
):
    """Генерирует `count` фейковых инцидентов пачками по `batch_size`."""
    print(f"Начинаю генерацию {count} инцидентов...")

    for i in range(0, count, batch_size):
        batch = []
        current_batch_size = min(batch_size, count - i)

        for j in range(current_batch_size):
            incident = Incident(
                description="",          # пустое описание
                status="open",           # фиксированный статус
                source="operator",       # фиксированный источник
                # Добавьте другие обязательные поля, если они есть!
                # Например: created_at=datetime.utcnow(), user_id=..., и т.д.
            )
            batch.append(incident)

        session.add_all(batch)
        await session.commit()  # коммитим каждую пачку

        print(f"Добавлено {i + current_batch_size} / {count}")

    print("✅ Генерация завершена!")


async def main():
    session_factory = create_session_factory(settings.DATABASE_URL)

    async with session_factory() as session:
        await generate_fake_incidents(session, count=100, batch_size=2000)


if __name__ == "__main__":
    asyncio.run(main())
