from typing import Type, Any

from chalifour.db.models import base


def verify_model_attributes(cls: Type[Any]) -> None:
    assert hasattr(cls, "id")


def test_all_base_model_attributes():
    for class_name in base.__all__:
        verify_model_attributes(getattr(base, class_name))
