"""модель инцидентов"""

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.enums import SourceDomain, StatusDomain
from .base import Base, StrNullFalse


class Incident(Base):
    description: Mapped[StrNullFalse]
    status: Mapped[StatusDomain] = mapped_column(
        SQLEnum(StatusDomain), default=StatusDomain.OPEN
    )
    source: Mapped[SourceDomain] = mapped_column(SQLEnum(SourceDomain), nullable=False)

    # def __str__(self):
    #     return f"{self.status.value} from {self.source.value}"
    #
    # def __repr__(self):
    #     return (
    #         f"<{self.__class__.__name__} "
    #         f"(id={self.id}, status={self.status.value}, source={self.source.value})>"
    #     )
