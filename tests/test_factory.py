"""
Unit tests for the factory module in modelrepo.

This module contains comprehensive tests for the get_repository function,
which dynamically imports and instantiates repository classes based on
configuration strings.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Any, Dict, Type, TypeVar

from modelrepo.factory import get_repository
from modelrepo.repository import ModelRepository


T = TypeVar("T")


class MockModel:
    """Mock model class for testing purposes."""

    def __init__(self, id: str = "", name: str = "test", value: int = 0):
        self.id = id
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, MockModel):
            return False
        return (
            self.id == other.id
            and self.name == other.name
            and self.value == other.value
        )


class MockRepository(ModelRepository[T]):
    """Mock repository class for testing purposes."""

    def __init__(self, model_class: Type[T], **kwargs):
        super().__init__(model_class)
        self.kwargs = kwargs
        self._storage = {}

    def create(self, model_data: Dict[str, Any]):
        return self.model_class(**model_data)

    def get_by_id(self, model_id: Any):
        return self._storage.get(model_id)

    def find_one(self, query: Dict[str, Any]):
        return None

    def find_all(self, query=None, limit=None, skip=None):
        return []

    def update(self, model_id: Any, update_data: Dict[str, Any]):
        return None

    def delete(self, model_id: Any) -> bool:
        return False

    def count(self, query=None) -> int:
        return 0


def test_successful_repository_creation(capsys):
    """Test successful creation of a repository with valid class path."""
    class_path = "tests.test_factory.MockRepository"
    kwargs = {"param1": "value1", "param2": "value2"}

    with patch("importlib.import_module") as mock_import:
        # Mock the module
        mock_module = Mock()
        mock_module.MockRepository = MockRepository
        mock_import.return_value = mock_module

        # Call the function
        result = get_repository(MockModel, class_path, kwargs)

        # Verify the result
        assert isinstance(result, MockRepository)
        assert result.model_class == MockModel
        assert result.kwargs == kwargs

        # Verify import was called correctly
        mock_import.assert_called_once_with("tests.test_factory")

        # Verify print output
        captured = capsys.readouterr()
        assert (
            "Using model repository class: tests.test_factory.MockRepository"
            in captured.out
        )


def test_repository_creation_with_empty_kwargs():
    """Test repository creation with empty kwargs."""
    class_path = "tests.test_factory.MockRepository"
    kwargs = {}

    with patch("importlib.import_module") as mock_import:
        mock_module = Mock()
        mock_module.MockRepository = MockRepository
        mock_import.return_value = mock_module

        result = get_repository(MockModel, class_path, kwargs)

        assert isinstance(result, MockRepository)
        assert result.model_class == MockModel
        assert result.kwargs == {}


def test_repository_creation_with_real_in_memory_repository(capsys):
    """Test with a real repository class from the codebase."""
    class_path = (
        "modelrepo.repository._in_memory_model_repository.InMemoryModelRepository"
    )
    kwargs = {}

    result = get_repository(MockModel, class_path, kwargs)

    # Should create an InMemoryModelRepository instance
    assert result is not None
    assert result.model_class == MockModel

    # Verify print output
    captured = capsys.readouterr()
    expected_output = "Using model repository class: modelrepo.repository._in_memory_model_repository.InMemoryModelRepository"
    assert expected_output in captured.out


def test_import_error_module_not_found(capsys):
    """Test ImportError when module cannot be imported."""
    class_path = "nonexistent.module.SomeRepository"
    kwargs = {}

    with patch("importlib.import_module") as mock_import:
        mock_import.side_effect = ImportError("No module named 'nonexistent'")

        with pytest.raises(ImportError, match="No module named 'nonexistent'"):
            get_repository(MockModel, class_path, kwargs)

        # Verify error message was printed
        captured = capsys.readouterr()
        assert (
            "Error importing class 'nonexistent.module.SomeRepository':" in captured.out
        )
        assert "No module named 'nonexistent'" in captured.out


def test_invalid_class_path_format():
    """Test with invalid class path format (no dots)."""
    class_path = "InvalidPath"
    kwargs = {}

    with pytest.raises(ValueError, match="not enough values to unpack"):
        get_repository(MockModel, class_path, kwargs)


def test_class_path_with_single_dot():
    """Test with class path containing only one dot."""
    class_path = "module.Class"
    kwargs = {}

    with patch("importlib.import_module") as mock_import:
        mock_module = Mock()
        mock_module.Class = MockRepository
        mock_import.return_value = mock_module

        result = get_repository(MockModel, class_path, kwargs)

        assert isinstance(result, MockRepository)
        mock_import.assert_called_once_with("module")


def test_class_path_with_multiple_dots():
    """Test with class path containing multiple dots."""
    class_path = "package.subpackage.module.Class"
    kwargs = {}

    with patch("importlib.import_module") as mock_import:
        mock_module = Mock()
        mock_module.Class = MockRepository
        mock_import.return_value = mock_module

        result = get_repository(MockModel, class_path, kwargs)

        assert isinstance(result, MockRepository)
        mock_import.assert_called_once_with("package.subpackage.module")


def test_kwargs_passed_to_repository_constructor():
    """Test that kwargs are properly passed to the repository constructor."""
    class_path = "tests.test_factory.MockRepository"
    kwargs = {"database_url": "sqlite:///test.db", "timeout": 30, "debug": True}

    with patch("importlib.import_module") as mock_import:
        mock_module = Mock()
        mock_module.MockRepository = MockRepository
        mock_import.return_value = mock_module

        result = get_repository(MockModel, class_path, kwargs)

        assert isinstance(result, MockRepository)
        assert result.kwargs == kwargs


def test_model_class_passed_correctly():
    """Test that model_class parameter is passed correctly."""

    class AnotherMockModel:
        def __init__(self, id: str = ""):
            self.id = id

    class_path = "tests.test_factory.MockRepository"
    kwargs = {}

    with patch("importlib.import_module") as mock_import:
        mock_module = Mock()
        mock_module.MockRepository = MockRepository
        mock_import.return_value = mock_module

        result = get_repository(AnotherMockModel, class_path, kwargs)

        assert result.model_class == AnotherMockModel


def test_generic_type_instantiation():
    """Test that the generic type is properly instantiated with [model_class]."""
    class_path = "tests.test_factory.MockRepository"
    kwargs = {}

    with patch("importlib.import_module") as mock_import:
        mock_module = Mock()

        # Create a mock class that tracks how it's called
        mock_repo_class = MagicMock()
        mock_repo_instance = MagicMock()

        # Set up the mock so that MockRepository[MockModel] returns a callable
        mock_repo_class.__getitem__.return_value = Mock(return_value=mock_repo_instance)
        mock_module.MockRepository = mock_repo_class
        mock_import.return_value = mock_module

        result = get_repository(MockModel, class_path, kwargs)

        # Verify that the class was accessed with [MockModel]
        mock_repo_class.__getitem__.assert_called_once_with(MockModel)

        # Verify that the constructor was called with correct parameters
        mock_repo_class.__getitem__.return_value.assert_called_once_with(
            model_class=MockModel, **kwargs
        )

        assert result == mock_repo_instance


@patch("builtins.print")
def test_print_statement_called(mock_print):
    """Test that the print statement is called with correct message."""
    class_path = "tests.test_factory.MockRepository"
    kwargs = {}

    with patch("importlib.import_module") as mock_import:
        mock_module = Mock()
        mock_module.MockRepository = MockRepository
        mock_import.return_value = mock_module

        get_repository(MockModel, class_path, kwargs)

        mock_print.assert_called_once_with("Using model repository class:", class_path)


def test_exception_handling_preserves_original_exception():
    """Test that original exceptions are preserved and re-raised."""
    class_path = "nonexistent.module.Class"
    kwargs = {}

    original_error = ImportError("Original error message")

    with patch("importlib.import_module") as mock_import:
        mock_import.side_effect = original_error

        with pytest.raises(ImportError) as exc_info:
            get_repository(MockModel, class_path, kwargs)

        # Verify the original exception is preserved
        assert exc_info.value is original_error


def test_empty_class_path_raises_error():
    """Test that empty class path raises appropriate error."""
    class_path = ""
    kwargs = {}

    with pytest.raises(ValueError):
        get_repository(MockModel, class_path, kwargs)


def test_none_class_path_raises_error():
    """Test that None class path raises appropriate error."""
    class_path = None
    kwargs = {}

    with pytest.raises(AttributeError):
        get_repository(MockModel, class_path, kwargs)


def test_repository_with_complex_kwargs():
    """Test repository creation with complex kwargs including nested structures."""
    class_path = "tests.test_factory.MockRepository"
    kwargs = {
        "config": {"host": "localhost", "port": 5432, "options": ["ssl", "auth"]},
        "retry_policy": {"max_retries": 3, "backoff_factor": 2.0},
        "simple_value": "test",
    }

    with patch("importlib.import_module") as mock_import:
        mock_module = Mock()
        mock_module.MockRepository = MockRepository
        mock_import.return_value = mock_module

        result = get_repository(MockModel, class_path, kwargs)

        assert isinstance(result, MockRepository)
        assert result.kwargs == kwargs
        # Verify nested structures are preserved
        assert result.kwargs["config"]["host"] == "localhost"
        assert result.kwargs["retry_policy"]["max_retries"] == 3
