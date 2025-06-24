"""
Tests for the InMemoryModelRepository class in the modelrepo.repository._in_memory_model_repository module.

This module tests the in-memory implementation of the ModelRepository interface,
which is primarily used for testing purposes. The tests ensure all CRUD operations
work correctly and that the repository behaves consistently with the interface
contract defined by the abstract base class.
"""

import pytest
from typing import Any
from uuid import uuid4

from modelrepo.repository._in_memory_model_repository import InMemoryModelRepository


class MockModel:
    """Mock model class for testing purposes."""

    def __init__(self, id: str = None, name: str = "test", value: int = 0):
        self.id = id or str(uuid4())
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, MockModel):
            return False
        return (
            self.id == other.id
            and self.name == other.name
            and self.value == other.value
        )


@pytest.fixture
def repository():
    """Create a fresh InMemoryModelRepository for each test."""
    return InMemoryModelRepository(MockModel)


@pytest.fixture
def sample_models():
    """Create sample models for testing."""
    return [
        MockModel(id="1", name="Alice", value=100),
        MockModel(id="2", name="Bob", value=200),
        MockModel(id="3", name="Charlie", value=300),
    ]


def test_repository_initialization(repository):
    """
    Test that InMemoryModelRepository initializes correctly.

    This test verifies that the repository is properly initialized with
    an empty storage dictionary and the correct model class.
    """
    assert repository.model_class == MockModel
    assert repository._storage == {}


def test_create_model(repository):
    """
    Test creating a new model in the repository.

    This test verifies that the create method properly stores a model
    and assigns a UUID if no ID is provided, returning the created model.
    """
    model_data = {"name": "Test User", "value": 42}

    result = repository.create(model_data)

    assert result.id is not None  # Should have an ID assigned
    assert result.name == "Test User"
    assert result.value == 42
    assert len(repository._storage) == 1


def test_create_model_with_existing_id(repository):
    """
    Test creating a model with a pre-existing ID.

    This test verifies that when a model already has an ID, the create
    method uses that ID instead of generating a new one.
    """
    model_data = {"id": "existing_id", "name": "Test", "value": 1}

    result = repository.create(model_data)

    assert result.id == "existing_id"
    assert repository._storage["existing_id"] == MockModel(**model_data)


def test_get_by_id_existing(repository, sample_models):
    """
    Test retrieving an existing model by ID.

    This test verifies that get_by_id correctly returns a model
    when it exists in the repository.
    """
    model = sample_models[0]
    repository._storage[model.id] = model

    result = repository.get_by_id(model.id)

    assert result == model


def test_get_by_id_nonexistent(repository):
    """
    Test retrieving a non-existent model by ID.

    This test verifies that get_by_id returns None when attempting
    to retrieve a model that doesn't exist in the repository.
    """
    result = repository.get_by_id("nonexistent_id")

    assert result is None


def test_find_one_matching(repository, sample_models):
    """
    Test finding a single model that matches query criteria.

    This test verifies that find_one correctly returns the first
    model that matches the provided query parameters.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    result = repository.find_one({"name": "Bob"})

    assert result == sample_models[1]  # Bob is the second model


def test_find_one_no_match(repository, sample_models):
    """
    Test finding a model when no matches exist.

    This test verifies that find_one returns None when no models
    match the provided query criteria.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    result = repository.find_one({"name": "David"})

    assert result is None


def test_find_one_multiple_criteria(repository, sample_models):
    """
    Test finding a model with multiple query criteria.

    This test verifies that find_one correctly matches models
    against multiple query parameters simultaneously.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    result = repository.find_one({"name": "Alice", "value": 100})

    assert result == sample_models[0]


def test_find_all_no_query(repository, sample_models):
    """
    Test finding all models without query criteria.

    This test verifies that find_all returns all models in the
    repository when no query is provided.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    results = repository.find_all()

    assert len(results) == 3
    assert all(model in results for model in sample_models)


def test_find_all_with_query(repository, sample_models):
    """
    Test finding all models that match query criteria.

    This test verifies that find_all correctly filters models
    based on the provided query parameters.
    """
    # Add models with some having the same value
    sample_models[2].value = 100  # Charlie now has same value as Alice
    for model in sample_models:
        repository._storage[model.id] = model

    results = repository.find_all({"value": 100})

    assert len(results) == 2
    assert sample_models[0] in results  # Alice
    assert sample_models[2] in results  # Charlie


def test_find_all_with_limit(repository, sample_models):
    """
    Test finding models with a limit on results.

    This test verifies that find_all respects the limit parameter
    and returns only the specified number of results.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    results = repository.find_all(limit=2)

    assert len(results) == 2


def test_find_all_with_skip(repository, sample_models):
    """
    Test finding models with pagination using skip parameter.

    This test verifies that find_all correctly skips the specified
    number of results, enabling pagination functionality.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    results = repository.find_all(skip=1)

    assert len(results) == 2  # Should skip first result


def test_find_all_with_limit_and_skip(repository, sample_models):
    """
    Test finding models with both limit and skip parameters.

    This test verifies that find_all correctly combines skip and limit
    parameters for proper pagination support.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    results = repository.find_all(skip=1, limit=1)

    assert len(results) == 1


def test_update_existing_model(repository, sample_models):
    """
    Test updating an existing model in the repository.

    This test verifies that update correctly modifies the specified
    fields of an existing model and returns the updated model.
    """
    model = sample_models[0]
    repository._storage[model.id] = model

    update_data = {"name": "Updated Alice", "value": 999}
    result = repository.update(model.id, update_data)

    assert result is not None
    assert result.name == "Updated Alice"
    assert result.value == 999
    assert result.id == model.id  # ID should remain unchanged


def test_update_nonexistent_model(repository):
    """
    Test updating a model that doesn't exist.

    This test verifies that update raises a ValueError when attempting
    to update a model that doesn't exist in the repository.
    """
    with pytest.raises(ValueError, match="Model with ID nonexistent_id not found"):
        repository.update("nonexistent_id", {"name": "New Name"})


def test_delete_existing_model(repository, sample_models):
    """
    Test deleting an existing model from the repository.

    This test verifies that delete successfully removes a model
    from the repository and returns True.
    """
    model = sample_models[0]
    repository._storage[model.id] = model

    result = repository.delete(model.id)

    assert result is True
    assert model.id not in repository._storage


def test_delete_nonexistent_model(repository):
    """
    Test deleting a model that doesn't exist.

    This test verifies that delete raises a ValueError when attempting
    to delete a model that doesn't exist in the repository.
    """
    with pytest.raises(ValueError, match="Model with ID nonexistent_id not found"):
        repository.delete("nonexistent_id")


def test_count_all_models(repository, sample_models):
    """
    Test counting all models in the repository.

    This test verifies that count returns the correct total number
    of models when no query is provided.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    result = repository.count()

    assert result == 3


def test_count_with_query(repository, sample_models):
    """
    Test counting models that match query criteria.

    This test verifies that count correctly filters and counts
    models based on the provided query parameters.
    """
    # Make two models have the same value
    sample_models[1].value = 100  # Bob now has same value as Alice
    for model in sample_models:
        repository._storage[model.id] = model

    result = repository.count({"value": 100})

    assert result == 2


def test_clear_repository(repository, sample_models):
    """
    Test clearing all models from the repository.

    This test verifies that the clear method removes all models
    from the repository storage.
    """
    for model in sample_models:
        repository._storage[model.id] = model

    repository.clear()

    assert len(repository._storage) == 0
    assert repository.count() == 0


def test_find_all_with_nonexistent_attribute(repository):
    """
    Test querying for a non-existent attribute.

    This test verifies that find_all handles queries for attributes
    that don't exist on the model objects gracefully.
    """
    model = MockModel(id="1", name="Test")
    repository._storage[model.id] = model

    results = repository.find_all({"nonexistent_attr": "value"})

    assert len(results) == 0


def test_repository_isolation(repository):
    """
    Test that repository instances are properly isolated.

    This test verifies that different repository instances don't
    share storage, ensuring proper isolation between tests.
    """
    repository1 = InMemoryModelRepository(MockModel)
    repository2 = InMemoryModelRepository(MockModel)

    repository1.create({"id": "1", "name": "Test"})

    assert len(repository1._storage) == 1
    assert len(repository2._storage) == 0
