"""
Base model classes for different database backends.

This module provides the foundational model classes that serve as base classes
for database-specific models in the Chalifour database system. It includes base
classes for SQL databases (using SQLAlchemy) and MongoDB.
"""

from dataclasses import dataclass
from sqlalchemy import Column, Integer

from chalifour.db.repository._sql_alchemy_model_repository import Base


class SQLModel(Base):
    """
    Base class for all SQL database models.

    This abstract class extends SQLAlchemy's declarative base and provides
    common functionality for all SQL-based models. It defines a standard
    primary key 'id' column that all derived models will inherit.

    Attributes:
        id (Column): Integer primary key column that auto-increments
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True)


@dataclass
class MongoDBModel:
    """
    Base class for all MongoDB models.

    This class provides a consistent interface for MongoDB documents.
    It uses the standard MongoDB '_id' field and provides a property
    to access it as 'id' for consistency with other model types.

    Attributes:
        _id (str): MongoDB document identifier
    """

    _id: str

    @property
    def id(self):
        """
        Property that provides access to the MongoDB document ID.

        Returns:
            str: The document's MongoDB identifier
        """
        return self._id


__all__ = ["SQLModel", "MongoDBModel"]
