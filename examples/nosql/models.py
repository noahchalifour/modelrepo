from chalifour.db.registry import registered_model
from chalifour.db.models.base import MongoDBModel

from dataclasses import dataclass


@registered_model
@dataclass
class User(MongoDBModel):
    name: str
    email: str

    def __repr__(self) -> str:
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"
