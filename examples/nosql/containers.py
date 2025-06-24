from dependency_injector import containers, providers
from modelrepo.factory import get_repository

from models import User


class ModelRepositoriesContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    repository_factory = providers.Factory(
        get_repository,
        class_path=config.class_path,
        kwargs=config.args,
    )

    user_repository = providers.Singleton(repository_factory, User)


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["./config.yml"])
    wiring_config = containers.WiringConfiguration(modules=["__main__"])

    model_repositories_container = providers.Container(
        ModelRepositoriesContainer,
        config=config.model_repository,
    )
