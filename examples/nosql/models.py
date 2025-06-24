from modelrepo.models.base import MongoDBModel

from dataclasses import dataclass


@dataclass
class User(MongoDBModel):
    name: str
    email: str

    def __repr__(self) -> str:
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"
