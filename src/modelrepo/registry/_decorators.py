from typing import Type, Any

from ._model_repository_registry import _deferred_registered_models


def registered_model(cls: Type[Any]) -> Type[Any]:
    """
    Decorator to automatically register a model's repository with the global RepositoryRegistry.
    """

    _deferred_registered_models.append(cls)

    return cls
