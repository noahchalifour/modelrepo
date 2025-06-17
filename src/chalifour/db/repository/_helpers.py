from typing import Type

from ._model_repository import ModelRepository


def get_repository_class_from_path(class_path: str) -> Type[ModelRepository]:
    from ._sql_alchemy_model_repository import SQLAlchemyModelRepository

    return SQLAlchemyModelRepository
