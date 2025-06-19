"""
Tests for the decorator functionality in the chalifour.db.registry module.

This module tests the model registration decorators that allow models to be
automatically registered with the model repository registry system. These
decorators are a key part of the database abstraction layer, enabling models
to be discovered and managed by the appropriate repositories.
"""

from chalifour.db.registry._model_repository_registry import _deferred_registered_models
from chalifour.db import registry


def test_registered_model_decorator():
    """
    Test that the @registered_model decorator properly registers model classes.

    This test verifies that when a class is decorated with @registered_model,
    it gets added to the _deferred_registered_models collection for later
    registration with the actual model registry container. This deferred
    registration pattern allows models to be defined before the container
    is initialized.
    """

    @registry.registered_model
    class _:
        pass

    assert len(_deferred_registered_models) == 1, (
        "Model was not added to deferred registration list"
    )
