from typing import Type, Any

from chalifour.db.models import base


def verify_model_attributes(model: Any) -> None:
    assert hasattr(model, "id")


def verify_model_constructor(cls: Type[Any]) -> Any:
    return cls(id="0")


def verify_model_class(cls: Type[Any]) -> None:
    model = verify_model_constructor(cls)
    verify_model_attributes(model)


def test_all_base_model_attributes():
    for class_name in base.__all__:
        verify_model_class(getattr(base, class_name))


def test_mongodb_model_identifier():
    mongo_model = base.MongoDBModel(_id="0")

    verify_model_attributes(mongo_model)
