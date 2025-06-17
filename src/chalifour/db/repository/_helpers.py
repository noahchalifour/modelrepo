"""
Helper functions for repository management.

This module provides utility functions for dynamically loading and managing
repository classes in the chalifour.db package.
"""

from typing import Type
import importlib

from ._model_repository import ModelRepository


def get_repository_class_from_path(class_path: str) -> Type[ModelRepository]:
    """
    Dynamically import and return a ModelRepository class from a fully qualified path.

    This function allows for dynamic loading of repository implementations based on
    configuration, enabling flexible repository selection without hard-coded dependencies.

    Args:
        class_path: A string representing the fully qualified path to the repository class
                   (e.g., "chalifour.db.repository.MongoDBModelRepository")

    Returns:
        The ModelRepository class referenced by the path

    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the class does not exist in the specified module

    Example:
        >>> repo_class = get_repository_class_from_path("chalifour.db.repository.MongoDBModelRepository")
        >>> repo_instance = repo_class(model_type=MyModel)
    """
    print("Using model repository class:", class_path)

    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        my_class = getattr(module, class_name)
        return my_class
    except (ImportError, AttributeError) as e:
        print(f"Error importing class '{class_path}': {e}")
        raise
