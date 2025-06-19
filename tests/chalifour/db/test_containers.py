"""
Tests for the container classes in the chalifour.db.containers module.

This module tests the functionality of the container classes, particularly
the ModelRegistryContainer, to ensure they provide the expected interface
and behavior for dependency injection and model registry management.
"""

from chalifour.db import containers


def test_model_registry_container_attributes():
    """
    Test that the ModelRegistryContainer has all required attributes.

    This test verifies that the ModelRegistryContainer initializes with
    all the necessary components for proper operation, including:
    - config: Configuration settings
    - wiring_config: Dependency injection wiring configuration
    - model_repository_factory: Factory for creating model repositories
    - registry: Registry for storing and retrieving model classes
    """
    container = containers.ModelRegistryContainer()

    assert hasattr(container, "config"), (
        "ModelRegistryContainer missing 'config' attribute"
    )
    assert hasattr(container, "wiring_config"), (
        "ModelRegistryContainer missing 'wiring_config' attribute"
    )
    assert hasattr(container, "model_repository_factory"), (
        "ModelRegistryContainer missing 'model_repository_factory' attribute"
    )
    assert hasattr(container, "registry"), (
        "ModelRegistryContainer missing 'registry' attribute"
    )
