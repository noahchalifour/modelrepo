"""
Helper functions for repository management.

This module provides utility functions for dynamically loading and managing
repository classes in the modelrepo package.
"""

from typing import Type
from dependency_injector.providers import Configuration
import importlib

from ._model_repository import ModelRepository


def get_repository_factory(cfg: Configuration) -> Type[ModelRepository]:
    """
    Dynamically import and return a ModelRepository factory from a fully qualified path.

    This function allows for dynamic loading of repository implementations based on
    configuration, enabling flexible repository selection without hard-coded dependencies.

    Args:
        class_path: A string representing the fully qualified path to the repository class
                   (e.g., "modelrepo.repository.MongoDBModelRepository")

    Returns:
        The factory to create the ModelRepository referenced by the path

    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the class does not exist in the specified module

    Example:
        >>> repo_factory = get_repository_factory(config)
        >>> repo_instance = repo_factory(model_type=MyModel)
    """
    class_path = cfg.get("class_path")

    print("Using model repository class:", class_path)

    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        my_class = getattr(module, class_name)
        return my_class.get_repository_factory(cfg)
    except (ImportError, AttributeError) as e:
        print(f"Error importing class '{class_path}': {e}")
        raise
