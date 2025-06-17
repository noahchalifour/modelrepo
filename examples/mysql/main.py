from dependency_injector.wiring import inject, Provide
from chalifour.db.registry import ModelRepositoryRegistry

from containers import ApplicationContainer
from models import User


@inject
def initialize(
    model_repository_registry: ModelRepositoryRegistry = Provide[
        ApplicationContainer.model_repository.registry
    ],
):
    model_repository_registry.register_deferred_models()


@inject
def main(
    model_repository_registry: ModelRepositoryRegistry = Provide[
        ApplicationContainer.model_repository.registry
    ],
):
    r = model_repository_registry.get_repository(User)

    existing_model = r.find_one({"email": "test@email.com"})
    if existing_model:
        r.delete(existing_model.id)
        print("Deleted existing model:", existing_model)

    user = r.create({"name": "John Doe", "email": "test@email.com"})
    print("Created user:", user)


if __name__ == "__main__":
    ApplicationContainer()

    initialize()
    main()
