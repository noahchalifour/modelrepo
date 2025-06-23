from typing import TypeVar, Dict, Any, Type, Callable
from dependency_injector.wiring import inject

from modelrepo.repository import ModelRepository


T = TypeVar("T")
_deferred_registered_models = []


class ModelRepositoryRegistry:
    """
    Registry for managing model repositories.

    This class provides a centralized registry for model repositories, allowing
    different model types to be associated with their respective repository instances.
    It supports automatic repository creation through a factory pattern and provides
    lookup functionality to retrieve repositories by model type.

    The registry is useful for dependency injection scenarios where repositories
    need to be accessed throughout the application without creating new instances.
    """

    _repositories: Dict[
        Type[Any], ModelRepository[Any]
    ] = {}  # Use Any for TypeVar within registry itself

    _model_repository_factory: Callable[[Any], ModelRepository[Any]]

    @inject
    def __init__(
        self,
        model_repository_factory: Callable[[Any], ModelRepository[Any]],
    ) -> None:
        """
        Initialize the ModelRepositoryRegistry.

        Args:
            model_repository_factory: A factory function that creates repository
                instances for a given model type. This function should accept a
                model type and return a ModelRepository instance for that type.
        """
        self._model_repository_factory = model_repository_factory

    def register_deferred_models(self) -> None:
        """
        Register all models that were decorated with @register_model but deferred until container initialization.

        This function processes models that were marked for registration via decorators
        but couldn't be registered immediately due to dependency injection timing.
        It's called after the container is fully initialized to ensure all dependencies
        are available.

        Raises:
            Exception: For any errors during registration
        """
        # We ensure this runs *after* the container is fully initialized
        for model_cls in _deferred_registered_models:
            try:
                self.register_model(model_cls)
            except Exception as e:
                print(
                    f"Error during repository registration for {model_cls.__name__}: {e}"
                )
                raise

        _deferred_registered_models.clear()  # Optional: Clear the list after registration

    def register_model(self, model_type: Type[T]):
        """
        Register a model type by creating and registering a repository for it.

        This method uses the factory function provided during initialization
        to create a repository instance for the given model type.

        Args:
            model_type: The model class to register.
        """
        self.register_repository(
            model_type,
            self._model_repository_factory(model_type),
        )

    def register_repository(
        self,
        model_type: Type[T],
        repository_instance: ModelRepository[T],
    ):
        """
        Register a repository instance for a specific model type.

        This method allows manual registration of custom repository instances
        for specific model types.

        Args:
            model_type: The model class to register.
            repository_instance: The repository instance to associate with the model type.
        """
        self._repositories[model_type] = repository_instance
        print(f"Registered repository for model '{model_type.__name__}'")

    def get_repository(self, model_type: Type[T]) -> ModelRepository[T]:
        """
        Retrieve the repository instance for a specific model type.

        Args:
            model_type: The model class to get the repository for.

        Returns:
            The repository instance associated with the model type.

        Raises:
            Exception: If no repository is registered for the given model type.
        """
        if model_type in self._repositories:
            return self._repositories[model_type]
        print(f"No repository found for model '{model_type.__name__}'")
        raise KeyError(
            f"No repository registered for model type: {model_type.__name__}"
        )
