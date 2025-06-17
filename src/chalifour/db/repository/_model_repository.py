import abc
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type

# Define a TypeVar for your models. This makes the ModelRepository generic.
# T will represent the specific model class (e.g., User, Product, Order)
T = TypeVar("T")


class ModelRepository(Generic[T], abc.ABC):
    """
    Abstract base class for a generic model repository.
    Defines common CRUD operations for any model type.

    Attributes:
        model_class: Wrapper class for the model object
    """

    def __init__(self, model_class: Type[T]) -> None:
        self.model_class = model_class

    @abc.abstractmethod
    def create(self, model_data: Dict[str, Any]) -> Optional[T]:
        """
        Creates a new model instance in the database.
        :param model_data: A dictionary containing the data for the new model.
        :return: The created model instance or None if creation fails (e.g., due to duplicate key).
        """
        pass

    @abc.abstractmethod
    def get_by_id(self, model_id: Any) -> Optional[T]:
        """
        Retrieves a model instance by its ID.
        The type of model_id will depend on the database (e.g., int for SQL, ObjectId for MongoDB).
        :param model_id: The unique identifier of the model.
        :return: The model instance or None if not found.
        """
        pass

    @abc.abstractmethod
    def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """
        Finds a single model instance based on a query.
        The query format will vary by database.
        :param query: A dictionary representing the search criteria.
        :return: A single model instance or None if not found.
        """
        pass

    @abc.abstractmethod
    def find_all(
        self,
        query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[T]:
        """
        Finds all model instances matching a query, with optional pagination.
        :param query: Optional dictionary representing the search criteria. If None, retrieves all.
        :param limit: Maximum number of results to return.
        :param skip: Number of results to skip (for pagination).
        :return: A list of model instances.
        """
        pass

    @abc.abstractmethod
    def update(self, model_id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Updates an existing model instance.
        :param model_id: The ID of the model to update.
        :param update_data: A dictionary containing the fields to update and their new values.
        :return: The updated model instance or None if not found/updated.
        """
        pass

    @abc.abstractmethod
    def delete(self, model_id: Any) -> bool:
        """
        Deletes a model instance by its ID.
        :param model_id: The ID of the model to delete.
        :return: True if the model was deleted, False otherwise.
        """
        pass

    @abc.abstractmethod
    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Counts the number of model instances matching a query.
        :param query: Optional dictionary representing the search criteria.
        :return: The number of matching instances.
        """
        pass
