"""In-memory data stores for the demo.

Replace with PostgreSQL + SQLAlchemy in production.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from app.core.security import hash_password, verify_password


@dataclass
class User:
    id: int
    email: str
    full_name: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, email: str, full_name: str, password: str) -> "User":
        return cls(
            id=UserStore.next_id(),
            email=email.lower(),
            full_name=full_name,
            password_hash=hash_password(password),
        )

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)


class UserStore:
    _users: ClassVar[dict[int, User]] = {}
    _by_email: ClassVar[dict[str, User]] = {}
    _next_id: ClassVar[int] = 1

    @classmethod
    def next_id(cls) -> int:
        current = cls._next_id
        cls._next_id += 1
        return current

    @classmethod
    def get_by_id(cls, user_id: int) -> User | None:
        return cls._users.get(user_id)

    @classmethod
    def get_by_email(cls, email: str) -> User | None:
        return cls._by_email.get(email.lower())

    @classmethod
    def add(cls, user: User) -> None:
        cls._users[user.id] = user
        cls._by_email[user.email] = user

    @classmethod
    def exists(cls, email: str) -> bool:
        return email.lower() in cls._by_email


@dataclass
class PredictionRecord:
    prediction_id: int
    user_id: int
    filename: str
    image_path: str
    prediction: str | None = None  # "Cancer" | "Non-Cancer" | None
    confidence: float | None = None
    heatmap_path: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_pending(self) -> bool:
        return self.prediction is None


class PredictionStore:
    _records: ClassVar[dict[int, PredictionRecord]] = {}
    _by_user: ClassVar[dict[int, list[int]]] = {}
    _next_id: ClassVar[int] = 1

    @classmethod
    def next_id(cls) -> int:
        current = cls._next_id
        cls._next_id += 1
        return current

    @classmethod
    def create(cls, user_id: int, filename: str, image_path: str) -> PredictionRecord:
        record = PredictionRecord(
            prediction_id=cls.next_id(),
            user_id=user_id,
            filename=filename,
            image_path=image_path,
        )
        cls._records[record.prediction_id] = record
        cls._by_user.setdefault(user_id, []).insert(0, record.prediction_id)
        return record

    @classmethod
    def get(cls, prediction_id: int) -> PredictionRecord | None:
        return cls._records.get(prediction_id)

    @classmethod
    def get_by_user(cls, user_id: int) -> list[PredictionRecord]:
        ids = cls._by_user.get(user_id, [])
        return [cls._records[pid] for pid in ids if pid in cls._records]

    @classmethod
    def update_result(cls, prediction_id: int, prediction: str, confidence: float, heatmap_path: str | None = None) -> PredictionRecord | None:
        record = cls._records.get(prediction_id)
        if record:
            record.prediction = prediction
            record.confidence = confidence
            record.heatmap_path = heatmap_path
        return record