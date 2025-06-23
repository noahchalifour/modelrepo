"""
Tests for the base model classes in the modelrepo.models.base module.

This module tests the functionality of all base model classes to ensure they
conform to the expected interface and behavior, particularly focusing on:
- The presence of required attributes like 'id'
- Proper constructor behavior
- Consistent interface across different model types
"""

from typing import Type, Any

from modelrepo.models import base


def verify_model_attributes(model: Any) -> None:
    """
    Verify that a model instance has all required attributes.

    Args:
        model (Any): The model instance to verify
    """
    assert hasattr(model, "id"), (
        f"Model {type(model).__name__} is missing 'id' attribute"
    )


def verify_model_constructor(cls: Type[Any]) -> Any:
    """
    Create a model instance using the constructor with an ID parameter.

    This tests that models can be instantiated with an 'id' parameter,
    which should be properly handled by the constructor.

    Args:
        cls (Type[Any]): The model class to instantiate

    Returns:
        Any: An instance of the model class
    """
    return cls(id="0")


def verify_model_class(cls: Type[Any]) -> None:
    """
    Verify that a model class meets all requirements.

    This function tests both the constructor and the resulting instance
    to ensure the model class behaves as expected.

    Args:
        cls (Type[Any]): The model class to verify
    """
    model = verify_model_constructor(cls)
    verify_model_attributes(model)


def test_all_base_model_attributes():
    """
    Test that all model classes in the base module have the required attributes.

    This test dynamically checks all classes exported in the base.__all__ list
    to ensure they conform to the expected interface.
    """
    for class_name in base.__all__:
        verify_model_class(getattr(base, class_name))


def test_mongodb_model_identifier():
    """
    Test the MongoDB model's identifier handling.

    This test specifically verifies that the MongoDBModel correctly handles
    the MongoDB-style '_id' field and exposes it through the 'id' property.
    """
    mongo_model = base.MongoDBModel(_id="0")
    verify_model_attributes(mongo_model)
