from typing import TypeVar, Optional, List, Dict, Any, Type, Callable
from dependency_injector.wiring import inject, Provide

from chalifour.db.repository import ModelRepository


T = TypeVar("T")


class ModelRepositoryRegistry:
    _models: List[Any] = []
    _repositories: Dict[
        Type[Any], ModelRepository[Any]
    ] = {}  # Use Any for TypeVar within registry itself

    _model_repository_factory: Callable[[Any], ModelRepository[Any]]

    @inject
    def __init__(
        self,
        model_repository_factory: Callable[[Any], ModelRepository[Any]],
    ) -> None:
        self._model_repository_factory = model_repository_factory

    def register_model(self, model_type: Type[T]):
        self.register_repository(
            model_type,
            self._model_repository_factory(model_type),
        )

    def register_repository(
        self,
        model_type: Type[T],
        repository_instance: ModelRepository[T],
    ):
        self._repositories[model_type] = repository_instance
        print(f"Registered repository for model '{model_type.__name__}'")

    def get_repository(self, model_type: Type[T]) -> Optional[ModelRepository[T]]:
        if model_type in self._repositories:
            return self._repositories[model_type]
        print(f"No repository found for model '{model_type.__name__}'")
        return None


@inject
def registered_model(model_repository_registry: ModelRepositoryRegistry):
    """
    Decorator to automatically register a model's manager with the global RepositoryRegistry.
    """

    def decorator(model_class: Type[T]) -> Type[T]:
        try:
            model_repository_registry.register_model(model_class)
        except TypeError as e:
            print(f"Error instantiating manager for {model_class.__name__}: {e}")
            raise
        except Exception as e:
            print(
                f"Unexpected error during manager registration for {model_class.__name__}: {e}"
            )
            raise

        return model_class  # Return the original class unchanged

    return decorator
