"""встроенные справочники"""

from enum import Enum


class SourceDomain(str, Enum):
    OPERATOR = "operator"
    MONITORING = "monitoring"
    PARTNER = "partner"
    OTHER = "other"


class StatusDomain(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    RESOLVED = "resolved"
