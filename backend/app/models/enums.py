from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class TaskPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class TaskSource(StrEnum):
    MANUAL = "MANUAL"
    GOOGLE_CALENDAR = "GOOGLE_CALENDAR"
    CLASSROOM_BRIDGE = "CLASSROOM_BRIDGE"
