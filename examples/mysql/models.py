from modelrepo.registry import registered_model
from modelrepo.models.base import SQLModel

from sqlalchemy import String, Column


@registered_model
class User(SQLModel):
    __tablename__ = "users"

    name = Column(String)
    email = Column(String)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"
