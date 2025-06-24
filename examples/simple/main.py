from modelrepo.repository import InMemoryModelRepository
from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str
    email: str


def main():
    repository = InMemoryModelRepository(User)
    user = repository.create({"name": "John Doe", "email": "test@email.com"})
    print("Created user:", user)


if __name__ == "__main__":
    main()
