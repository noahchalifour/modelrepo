from dependency_injector import containers, providers

from chalifour.db.containers import ModelRegistryContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(ini_files=["./config.ini"])
    wiring_config = containers.WiringConfiguration(
        modules=[
            "__main__",
        ],
    )

    model_repository = providers.Container(
        ModelRegistryContainer,
        config=config.model_repository,
    )
