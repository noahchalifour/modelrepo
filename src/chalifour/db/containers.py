"""
Dependency injection containers for the Chalifour database module.

This module provides dependency injection containers that manage the lifecycle
and dependencies of database components, particularly the model repository registry.
It leverages the dependency_injector library to implement IoC (Inversion of Control)
patterns for better testability and modularity.
"""

from dependency_injector import containers, providers

from .registry import ModelRepositoryRegistry
from .repository._helpers import get_repository_class_from_path


class ModelRegistryContainer(containers.DeclarativeContainer):
    """
    Dependency injection container for the model registry system.

    This container manages the lifecycle of the ModelRepositoryRegistry and its dependencies.
    It provides configuration-based repository class loading, factory creation, and
    handles the registration of models that were deferred during application startup.

    Attributes:
        config: Configuration provider for container settings
        wiring_config: Configuration for dependency injection wiring
        model_repository_class: Provider that dynamically loads the repository class
        model_repository_factory: Factory provider for creating repository instances
        registry: Singleton provider for the ModelRepositoryRegistry
        register_models: Provider that triggers registration of deferred models
    """

    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        packages=[
            "chalifour.db.registry",
        ],
    )

    model_repository_class = providers.Callable(
        get_repository_class_from_path,
        class_path=config.class_path,
    )

    model_repository_factory = providers.Factory(model_repository_class)

    registry = providers.Singleton(
        ModelRepositoryRegistry,
        model_repository_factory=model_repository_factory,
    )
