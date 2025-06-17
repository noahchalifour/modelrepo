from dependency_injector import containers, providers

from chalifour.db.repository import ModelRepository
from chalifour.db.repository._helpers import get_repository_class_from_path
from ._model_repository_registry import ModelRepositoryRegistry


class ModelRepositoryRegistryContainer(containers.DeclarativeContainer):
    model_repository_class_path = providers.Dependency()

    model_repository_class = providers.Callable(
        get_repository_class_from_path,
        class_path=model_repository_class_path,
    )

    model_repository_factory = providers.Factory(model_repository_class)

    registry = providers.Singleton(
        ModelRepositoryRegistry,
        model_repository_factory=model_repository_factory,
    )
