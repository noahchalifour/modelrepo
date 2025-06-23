"""
Tests for the ModelRepositoryRegistry class.

This module contains tests for the ModelRepositoryRegistry class, which is responsible
for managing model repositories in the application. The registry provides a centralized
way to register and retrieve repositories for different model classes.

The tests verify:
1. Registration of models through different mechanisms (direct, deferred)
2. Repository retrieval functionality
3. Error handling for invalid operations
4. Integration with the repository factory pattern
"""

from typing import Type, Any
import pytest

from modelrepo.registry import ModelRepositoryRegistry
from modelrepo.repository import InMemoryModelRepository
from modelrepo.registry._decorators import _deferred_registered_models


@pytest.fixture
def model_repository_registry():
    """
    Create a ModelRepositoryRegistry fixture for testing.

    Returns:
        ModelRepositoryRegistry: A registry instance configured with InMemoryModelRepository
        as the factory for creating new repositories.
    """
    return ModelRepositoryRegistry(
        model_repository_factory=InMemoryModelRepository,
    )


class TestModel:
    """A simple test model class used for testing repository registration."""

    pass


def add_deferred_model():
    """
    Add TestModel to the list of deferred registered models.

    This simulates the behavior of the @register_model decorator without
    actually using the decorator in the test.
    """
    _deferred_registered_models.append(TestModel)


def verify_repository(
    model_repository_registry: ModelRepositoryRegistry, cls: Type[Any]
) -> None:
    """
    Verify that a repository for the given class exists in the registry and has the expected properties.

    Args:
        model_repository_registry: The registry to check
        cls: The model class to verify repository for

    Raises:
        AssertionError: If the repository doesn't exist or doesn't have the expected properties
    """
    repository = model_repository_registry.get_repository(cls)

    assert repository is not None, f"Repository for {cls.__name__} should not be None"
    assert isinstance(repository, InMemoryModelRepository), (
        f"Repository should be an instance of InMemoryModelRepository, got {type(repository).__name__}"
    )
    assert repository.model_class == cls, (
        f"Repository model_class should be {cls.__name__}, got {repository.model_class.__name__}"
    )


def test_register_deferred_models(model_repository_registry: ModelRepositoryRegistry):
    """
    Test that deferred models can be registered with the registry.

    This test verifies that models added to the _deferred_registered_models list
    are properly registered when register_deferred_models() is called.
    """
    add_deferred_model()

    model_repository_registry.register_deferred_models()

    verify_repository(
        model_repository_registry=model_repository_registry,
        cls=TestModel,
    )


def test_register_deferred_models_error():
    """
    Test that register_deferred_models() raises TypeError when model_repository_factory is None.

    This test verifies the error handling when trying to register deferred models
    with a registry that doesn't have a valid factory.
    """
    add_deferred_model()

    registry_with_error = ModelRepositoryRegistry(
        model_repository_factory=None,
    )

    with pytest.raises(TypeError):
        registry_with_error.register_deferred_models()


def test_register_model(model_repository_registry: ModelRepositoryRegistry):
    """
    Test direct registration of a model with the registry.

    This test verifies that a model can be registered directly with the registry
    using the register_model method, and that a repository is created for it.
    """
    model_repository_registry.register_model(TestModel)

    verify_repository(
        model_repository_registry=model_repository_registry,
        cls=TestModel,
    )


def test_register_repository(model_repository_registry: ModelRepositoryRegistry):
    """
    Test registration of a pre-created repository with the registry.

    This test verifies that a pre-created repository instance can be registered
    with the registry for a specific model class.
    """
    repository = InMemoryModelRepository(TestModel)

    model_repository_registry.register_repository(TestModel, repository)

    verify_repository(
        model_repository_registry=model_repository_registry,
        cls=TestModel,
    )


def test_get_repository_invalid(model_repository_registry: ModelRepositoryRegistry):
    """
    Test that get_repository raises KeyError for unregistered models.

    This test verifies that attempting to retrieve a repository for a model
    that hasn't been registered raises the appropriate exception.
    """

    class InvalidModel:
        pass

    with pytest.raises(KeyError, match="No repository registered for"):
        model_repository_registry.get_repository(InvalidModel)
