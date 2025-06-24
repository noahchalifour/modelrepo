from dependency_injector.wiring import inject, Provide
from modelrepo.repository import ModelRepository

from containers import ApplicationContainer
from models import User


@inject
def main(
    user_repository: ModelRepository[User] = Provide[
        ApplicationContainer.model_repositories_container.user_repository
    ],
):
    existing_user = user_repository.find_one(
        {"name": "John Doe", "email": "test@email.com"}
    )
    if existing_user:
        user_repository.delete(existing_user.id)
        print("Deleted existing user:", existing_user)

    user = user_repository.create({"name": "John Doe", "email": "test@email.com"})
    print("Created user:", user)


if __name__ == "__main__":
    ApplicationContainer()

    main()
