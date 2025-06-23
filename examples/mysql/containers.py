from dependency_injector import containers, providers

from modelrepo.containers import ModelRegistryContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["./config.yml"])
    wiring_config = containers.WiringConfiguration(
        modules=[
            "__main__",
        ],
    )

    model_repository = providers.Container(
        ModelRegistryContainer,
        config=config.model_repository,
    )
