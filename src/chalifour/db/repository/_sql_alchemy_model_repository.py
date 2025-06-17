from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from typing import Type, Any, Dict, List, Optional, TypeVar
import os

from ._model_repository import ModelRepository

T = TypeVar("T")
Base = declarative_base()


class SQLAlchemyModelRepository(ModelRepository[T]):
    """
    SQLAlchemy implementation of the ModelRepository interface.

    This class provides CRUD operations for SQLAlchemy models, handling session
    management and database interactions. It implements all abstract methods
    defined in the ModelRepository base class.

    Attributes:
        engine: SQLAlchemy engine instance connected to the database
        model_class: The SQLAlchemy model class this manager will operate on
        Session: SQLAlchemy sessionmaker factory for creating new sessions
    """

    def __init__(self, model_class: Type[T]):
        """
        Initialize the SQLAlchemy model manager.

        Args:
            db_uri: Database connection URI (e.g., 'sqlite:///database.db')
            model_class: The SQLAlchemy model class this manager will operate on
                         (must be a subclass of the declarative Base)

        Note:
            This constructor automatically creates the necessary tables in the database
            if they don't already exist.
        """
        super().__init__(model_class)

        db_uri = os.environ.get("SQL_ALCHEMY_DB_URI", "sqlite:///database.sqlite3")

        self.engine = create_engine(db_uri)
        Base.metadata.create_all(self.engine)  # Ensure table exists for this model
        self.Session = sessionmaker(bind=self.engine)

    def create(self, model_data: Dict[str, Any]) -> Optional[T]:
        """
        Creates a new model instance in the database.

        Args:
            model_data: Dictionary containing the data for the new model instance
                        with keys corresponding to model attributes

        Returns:
            The created model instance with any auto-generated fields populated,
            or None if creation fails (e.g., due to integrity constraints)

        Note:
            This method handles session management and automatically rolls back
            the transaction in case of IntegrityError.
        """
        session = self.Session()
        try:
            new_instance = self.model_class(**model_data)
            session.add(new_instance)
            session.commit()
            session.refresh(new_instance)  # Refresh to get auto-generated ID if any
            return new_instance
        except IntegrityError as e:
            session.rollback()
            print(f"SQLAlchemy create error: {e}")
            return None
        finally:
            session.close()

    def get_by_id(self, model_id: Any) -> Optional[T]:
        """
        Retrieves a model instance by its primary key ID.

        Args:
            model_id: The primary key value of the model to retrieve

        Returns:
            The model instance if found, or None if no model exists with the given ID
        """
        session = self.Session()
        try:
            return session.query(self.model_class).get(model_id)
        finally:
            session.close()

    def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """
        Finds a single model instance based on a query dictionary.

        Args:
            query: Dictionary of attribute-value pairs to filter by (exact matches only)
                  For example: {'name': 'John', 'active': True}

        Returns:
            The first matching model instance, or None if no match is found

        Note:
            This implementation uses SQLAlchemy's filter_by() for exact matches.
            For more complex queries (e.g., with operators like >, <, LIKE),
            a custom implementation would be needed.
        """
        session = self.Session()
        try:
            # SQLAlchemy queries are built differently than NoSQL.
            # We'll map dictionary query to filter_by or filter.
            # For simplicity, we'll use filter_by for exact matches here.
            # More complex queries might require using `filter` with `and_`, `or_` etc.
            return session.query(self.model_class).filter_by(**query).first()
        except Exception as e:
            print(f"SQLAlchemy find_one error: {e}")
            return None
        finally:
            session.close()

    def find_all(
        self,
        query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[T]:
        """
        Finds all model instances matching a query, with optional pagination.

        Args:
            query: Optional dictionary of attribute-value pairs to filter by.
                  If None, retrieves all instances of the model.
            limit: Maximum number of results to return (for pagination)
            skip: Number of results to skip (for pagination)

        Returns:
            A list of matching model instances, or an empty list if no matches
            or if an error occurs

        Example:
            # Get all active users, 10 per page, starting from the 2nd page
            users = manager.find_all({'active': True}, limit=10, skip=10)
        """
        session = self.Session()
        try:
            q = session.query(self.model_class)
            if query:
                q = q.filter_by(**query)  # Apply filters
            if skip is not None:
                q = q.offset(skip)
            if limit is not None:
                q = q.limit(limit)
            return q.all()
        except Exception as e:
            print(f"SQLAlchemy find_all error: {e}")
            return []
        finally:
            session.close()

    def update(self, model_id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Updates an existing model instance by ID.

        Args:
            model_id: The primary key of the model to update
            update_data: Dictionary containing the fields to update and their new values

        Returns:
            The updated model instance if found and updated successfully,
            or None if the model wasn't found or an error occurred

        Note:
            This method handles session management and automatically rolls back
            the transaction in case of IntegrityError (e.g., unique constraint violations).
        """
        session = self.Session()
        try:
            instance = session.query(self.model_class).get(model_id)
            if instance:
                for key, value in update_data.items():
                    setattr(instance, key, value)
                session.commit()
                session.refresh(instance)
                return instance
            return None
        except IntegrityError as e:
            session.rollback()
            print(f"SQLAlchemy update error: {e}")
            return None
        finally:
            session.close()

    def delete(self, model_id: Any) -> bool:
        """
        Deletes a model instance by its ID.

        Args:
            model_id: The primary key of the model to delete

        Returns:
            True if the model was found and deleted successfully,
            False if the model wasn't found
        """
        session = self.Session()
        try:
            instance = session.query(self.model_class).get(model_id)
            if instance:
                session.delete(instance)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Counts the number of model instances matching a query.

        Args:
            query: Optional dictionary of attribute-value pairs to filter by.
                  If None, counts all instances of the model.

        Returns:
            The number of matching instances

        Example:
            # Count all active users
            active_user_count = manager.count({'active': True})
        """
        session = self.Session()
        try:
            q = session.query(self.model_class)
            if query:
                q = q.filter_by(**query)
            return q.count()
        finally:
            session.close()
