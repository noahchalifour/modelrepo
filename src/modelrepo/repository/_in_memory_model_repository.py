"""
In-memory implementation of a model repository for testing purposes.

This module provides a simple in-memory implementation of the ModelRepository
interface that can be used in tests without requiring an actual database connection.
It stores models in memory and simulates basic CRUD operations.
"""

from typing import Dict, List, Optional, Any, Type
from uuid import uuid4

from ._model_repository import ModelRepository


T = Dict[str, Any]


class InMemoryModelRepository(ModelRepository[T]):
    """
    An in-memory implementation of ModelRepository for testing purposes.

    This repository stores models in an in-memory dictionary and simulates
    the behavior of a real database repository without actually connecting
    to any database. It's useful for unit tests that need to test code that
    depends on repositories without setting up actual database connections.

    Attributes:
        _storage (Dict[str, T]): In-memory storage for models
    """

    def __init__(self, model_class: Type[Any]) -> None:
        """
        Initialize an empty in-memory storage for models.

        Args:
            model_class: The class type of models to be stored in this repository.
                         Used for type checking and instantiation of models.
        """
        super().__init__(model_class)

        self._storage: Dict[str, T] = {}

    def get_by_id(self, model_id: Any) -> Optional[T]:
        """
        Retrieve a model by its ID.

        Args:
            model_id: The ID of the model to retrieve

        Returns:
            The model if found, None otherwise
        """
        return self._storage.get(model_id)

    def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """
        Find a single model matching the given query criteria.

        Args:
            query: Dictionary of attribute-value pairs to match against models

        Returns:
            A model if found, None otherwise

        Note:
            This method returns the first matching model found. If no models match
            the query, it will raise an IndexError.
        """
        results = self.find_all(query, limit=1)
        return results[0] if results else None

    def find_all(
        self,
        query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[T]:
        """
        Find models matching the given query criteria.

        Args:
            query: Dictionary of attribute-value pairs to match against models
            limit: Maximum number of results to return
            skip: Number of results to skip (for pagination)

        Returns:
            A list of models matching the query
        """
        if query is None:
            query = {}

        results = []
        for model in self._storage.values():
            matches = True
            for key, value in query.items():
                if not hasattr(model, key) or getattr(model, key) != value:
                    matches = False
                    break
            if matches:
                results.append(model)

        if skip is not None:
            results = results[skip:]

        if limit is not None:
            results = results[:limit]

        return results

    def create(self, model_data: Dict[str, Any]) -> Optional[T]:
        """
        Create a new model in the repository.

        If the model doesn't have an ID, a random UUID will be assigned.

        Args:
            model_data: The model to create

        Returns:
            The created model with its ID
        """
        # Assign an ID if not present
        if not hasattr(model_data, "id") or not getattr(model_data, "id"):
            setattr(model_data, "id", str(uuid4()))

        model_id = getattr(model_data, "id")
        self._storage[model_id] = model_data
        return model_data

    def update(self, model_id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing model in the repository.

        Args:
            model_id: The ID of the model to update
            update_data: Dictionary containing the fields to update and their new values

        Returns:
            The updated model

        Raises:
            ValueError: If the model with the specified ID doesn't exist
        """
        if model_id not in self._storage:
            raise ValueError(f"Model with ID {model_id} not found")

        model = self._storage[model_id]
        for key, value in update_data.items():
            setattr(model, key, value)
        return model

    def delete(self, model_id: Any) -> bool:
        """
        Delete a model from the repository.

        Args:
            model_id: The ID of the model to delete

        Returns:
            True if model was deleted, False otherwise

        Raises:
            ValueError: If the model doesn't exist
        """
        if model_id not in self._storage:
            raise ValueError(f"Model with ID {model_id} not found")

        del self._storage[model_id]
        return True

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count the number of models in the repository based on a query.

        Args:
            query: Optional dictionary of attribute-value pairs to filter models

        Returns:
            The number of models matching the query criteria
        """
        return len(self.find_all(query))

    def clear(self) -> None:
        """Clear all models from the repository."""
        self._storage.clear()
