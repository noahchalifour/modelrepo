"""
Tests for the base ModelRepository class in the modelrepo.repository._model_repository module.

This module tests the abstract base class functionality and the factory method
that creates repository instances with specific configurations. These tests
ensure the base repository interface works correctly and can be properly
extended by concrete implementations.
"""

from typing import Dict, Any, Optional, List, Type
import pytest
from unittest.mock import Mock

from modelrepo.repository._model_repository import ModelRepository


class MockModel:
    """Mock model class for testing purposes."""

    def __init__(self, id: str = "test_id", name: str = "test_name"):
        self.id = id
        self.name = name


class ConcreteModelRepository(ModelRepository[MockModel]):
    """
    Concrete implementation of ModelRepository for testing purposes.

    This class implements all abstract methods to allow testing of the
    base class functionality without needing actual database connections.
    """

    def __init__(
        self, model_class: Type[MockModel], test_config: str = "default", **kwargs
    ):
        super().__init__(model_class)
        self.test_config = test_config
        # Handle any additional config parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._storage: Dict[str, MockModel] = {}

    def create(self, model_data: Dict[str, Any]) -> Optional[MockModel]:
        """Create a mock model instance."""
        model = MockModel(**model_data)
        self._storage[model.id] = model
        return model

    def get_by_id(self, model_id: Any) -> Optional[MockModel]:
        """Get a mock model by ID."""
        return self._storage.get(model_id)

    def find_one(self, query: Dict[str, Any]) -> Optional[MockModel]:
        """Find one mock model matching query."""
        for model in self._storage.values():
            if all(getattr(model, k, None) == v for k, v in query.items()):
                return model
        return None

    def find_all(
        self,
        query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[MockModel]:
        """Find all mock models matching query."""
        if query is None:
            query = {}

        results = []
        for model in self._storage.values():
            if all(getattr(model, k, None) == v for k, v in query.items()):
                results.append(model)

        if skip:
            results = results[skip:]
        if limit:
            results = results[:limit]

        return results

    def update(self, model_id: Any, update_data: Dict[str, Any]) -> Optional[MockModel]:
        """Update a mock model."""
        if model_id in self._storage:
            for key, value in update_data.items():
                setattr(self._storage[model_id], key, value)
            return self._storage[model_id]
        return None

    def delete(self, model_id: Any) -> bool:
        """Delete a mock model."""
        if model_id in self._storage:
            del self._storage[model_id]
            return True
        return False

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count mock models matching query."""
        return len(self.find_all(query))


def test_model_repository_initialization():
    """
    Test that ModelRepository can be properly initialized with a model class.

    This test verifies that the base ModelRepository class correctly stores
    the model class during initialization and makes it available for use
    by concrete implementations.
    """
    repository = ConcreteModelRepository(MockModel)

    assert repository.model_class == MockModel
    assert hasattr(repository, "model_class")


def test_abstract_methods_cannot_be_instantiated():
    """
    Test that the abstract ModelRepository cannot be instantiated directly.

    This test verifies that attempting to instantiate the abstract base class
    directly raises a TypeError, ensuring that only concrete implementations
    can be created.
    """
    with pytest.raises(TypeError):
        # This should fail because ModelRepository is abstract
        ModelRepository(MockModel)
