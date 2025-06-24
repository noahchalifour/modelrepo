# ModelRepo

[![PyPI version](https://badge.fury.io/py/modelrepo.svg)](https://badge.fury.io/py/modelrepo)
[![Build Status](https://gitlab.chalifour.dev/noahchalifour/modelrepo/badges/main/pipeline.svg)](https://gitlab.chalifour.dev/noahchalifour/modelrepo/-/commits/main)
[![Coverage](https://gitlab.chalifour.dev/noahchalifour/modelrepo/badges/main/coverage.svg)](https://gitlab.chalifour.dev/noahchalifour/modelrepo/-/commits/main)
[![Python Versions](https://img.shields.io/pypi/pyversions/modelrepo.svg)](https://pypi.org/project/modelrepo/)
[![License](https://img.shields.io/pypi/l/modelrepo.svg)](https://pypi.org/project/modelrepo/)

A Python package for managing database models using model repositories.

## Features

- Easy to use
- Wide database support (In-memory, MySQL, MongoDB)
- Dependency injection using [dependency-injector](https://pypi.org/project/dependency-injector/)

## Installation

You can install ModelRepo using pip:

```bash
pip install modelrepo
```

For development installation:

```bash
git clone https://gitlab.chalifour.dev/noahchalifour/modelrepo.git
cd modelrepo
pip install -e ".[dev]"
```

## Quick Start

Here's a simple example to get you started:

```python
from modelrepo.repository import InMemoryModelRepository
from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str
    email: str


def main():
    repository: InMemoryModelRepository[User] = InMemoryModelRepository(User)
    user = repository.create({"name": "John Doe", "email": "test@email.com"})
    print("Created user:", user)


if __name__ == "__main__":
    main()
```

For more examples, see the [examples directory](examples/).

## Documentation

Documentation for the package can be found at <https://noahchalifour.github.io/modelrepo/reference/modelrepo/>

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://gitlab.chalifour.dev/noahchalifour/modelrepo.git
cd modelrepo

# Install development dependencies
pip install e ".[dev]"
```

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=src
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure your code follows the project's style guidelines and includes appropriate tests.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions and support, please open an issue on the GitLab repository.
