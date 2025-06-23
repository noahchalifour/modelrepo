"""
Tests for the SQLAlchemyModelRepository class in the modelrepo.repository._sql_alchemy_model_repository module.

This module tests the SQLAlchemy implementation of the ModelRepository interface,
ensuring all CRUD operations work correctly with SQLAlchemy-specific features like
session management, table creation, and integrity error handling. The tests use
mocking to avoid requiring a real database connection.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.exc import IntegrityError

from modelrepo.repository._sql_alchemy_model_repository import SQLAlchemyModelRepository


class MockModel:
    """Mock SQLAlchemy model class for testing."""
    def __init__(self, id: int = None, name: str = "test", value: int = 0, **kwargs):
        self.id = id
        self.name = name
        self.value = value
        # Store any additional kwargs as attributes
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __eq__(self, other):
        if not isinstance(other, MockModel):
            return False
        return (self.id == other.id and 
                self.name == other.name and 
                self.value == other.value)


@pytest.fixture
def mock_sqlalchemy_components():
    """Create mock SQLAlchemy components for testing."""
    with patch('modelrepo.repository._sql_alchemy_model_repository.create_engine') as mock_create_engine, \
         patch('modelrepo.repository._sql_alchemy_model_repository.sessionmaker') as mock_sessionmaker, \
         patch('modelrepo.repository._sql_alchemy_model_repository.Base') as mock_base:
        
        # Set up engine mock
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        # Set up session mock
        mock_session_class = Mock()
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_sessionmaker.return_value = mock_session_class
        
        # Set up base metadata mock
        mock_metadata = Mock()
        mock_base.metadata = mock_metadata
        
        yield {
            'create_engine': mock_create_engine,
            'engine': mock_engine,
            'sessionmaker': mock_sessionmaker,
            'session_class': mock_session_class,
            'session': mock_session,
            'base': mock_base,
            'metadata': mock_metadata
        }


@pytest.fixture
def repository(mock_sqlalchemy_components):
    """Create a SQLAlchemyModelRepository instance for testing."""
    return SQLAlchemyModelRepository("sqlite:///:memory:", MockModel)


def test_repository_initialization(mock_sqlalchemy_components):
    """
    Test that SQLAlchemyModelRepository initializes correctly with database connection.

    This test verifies that the repository properly creates the SQLAlchemy engine,
    sets up table creation, and configures the session factory.
    """
    repo = SQLAlchemyModelRepository("postgresql://user:pass@localhost/db", MockModel)
    
    # Verify engine was created with correct URI
    mock_sqlalchemy_components['create_engine'].assert_called_once_with("postgresql://user:pass@localhost/db")
    
    # Verify table creation was triggered
    mock_sqlalchemy_components['metadata'].create_all.assert_called_once_with(mock_sqlalchemy_components['engine'])
    
    # Verify sessionmaker was configured
    mock_sqlalchemy_components['sessionmaker'].assert_called_once_with(bind=mock_sqlalchemy_components['engine'])
    
    # Verify the repository has correct attributes
    assert repo.model_class == MockModel
    assert repo.engine == mock_sqlalchemy_components['engine']
    assert repo.Session == mock_sqlalchemy_components['session_class']


def test_create_success(repository, mock_sqlalchemy_components):
    """
    Test successful model creation in SQLAlchemy.

    This test verifies that create properly instantiates a model, adds it to
    the session, commits the transaction, and returns the created model.
    """
    mock_session = mock_sqlalchemy_components['session']
    
    # Mock the model constructor to return a proper instance
    mock_instance = Mock()
    mock_instance.id = 1
    mock_instance.name = "Created"
    mock_instance.value = 100
    
    with patch.object(repository, 'model_class', return_value=mock_instance) as mock_model_class:
        model_data = {"name": "Created", "value": 100}
        result = repository.create(model_data)
        
        # Verify model was instantiated with correct data
        mock_model_class.assert_called_once_with(**model_data)
        
        # Verify session operations
        mock_session.add.assert_called_once_with(mock_instance)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_instance)
        mock_session.close.assert_called_once()
        
        # Verify the result
        assert result == mock_instance


def test_create_integrity_error(repository, mock_sqlalchemy_components):
    """
    Test handling of integrity errors during creation.

    This test verifies that create returns None when an IntegrityError
    occurs, indicating a constraint violation (e.g., unique constraint).
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_session.commit.side_effect = IntegrityError("statement", "params", "orig")
    
    with patch('builtins.print') as mock_print:
        result = repository.create({"name": "Duplicate"})
        
        assert result is None
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_print.assert_called_once()
        assert "SQLAlchemy create error" in mock_print.call_args[0][0]


def test_get_by_id_success(repository, mock_sqlalchemy_components):
    """
    Test successful retrieval of a model by ID.

    This test verifies that get_by_id correctly queries the database
    using the session and returns the found model.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    
    expected_model = Mock()
    expected_model.id = 1
    expected_model.name = "Found"
    mock_query.get.return_value = expected_model
    
    result = repository.get_by_id(1)
    
    # Verify query operations
    mock_session.query.assert_called_once_with(MockModel)
    mock_query.get.assert_called_once_with(1)
    mock_session.close.assert_called_once()
    
    assert result == expected_model


def test_get_by_id_not_found(repository, mock_sqlalchemy_components):
    """
    Test retrieving a non-existent model by ID.

    This test verifies that get_by_id returns None when no model
    matches the provided ID.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.get.return_value = None
    
    result = repository.get_by_id(999)
    
    assert result is None
    mock_session.close.assert_called_once()


def test_find_one_success(repository, mock_sqlalchemy_components):
    """
    Test finding a single model with query criteria.

    This test verifies that find_one correctly applies filter_by
    criteria and returns the first matching model.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    
    expected_model = Mock()
    expected_model.id = 1
    expected_model.name = "Alice"
    mock_query.first.return_value = expected_model
    
    query = {"name": "Alice"}
    result = repository.find_one(query)
    
    # Verify query operations
    mock_session.query.assert_called_once_with(MockModel)
    mock_query.filter_by.assert_called_once_with(**query)
    mock_query.first.assert_called_once()
    mock_session.close.assert_called_once()
    
    assert result == expected_model


def test_find_one_not_found(repository, mock_sqlalchemy_components):
    """
    Test find_one when no models match the query.

    This test verifies that find_one returns None when no models
    match the provided query criteria.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.first.return_value = None
    
    result = repository.find_one({"name": "NonExistent"})
    
    assert result is None
    mock_session.close.assert_called_once()


def test_find_one_exception(repository, mock_sqlalchemy_components):
    """
    Test find_one when an exception occurs during query.

    This test verifies that find_one returns None and handles
    exceptions gracefully during query execution.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_session.query.side_effect = Exception("Database error")
    
    with patch('builtins.print') as mock_print:
        result = repository.find_one({"name": "Test"})
        
        assert result is None
        mock_session.close.assert_called_once()
        mock_print.assert_called_once()
        assert "SQLAlchemy find_one error" in mock_print.call_args[0][0]


def test_find_all_no_query(repository, mock_sqlalchemy_components):
    """
    Test finding all models without query criteria.

    This test verifies that find_all returns all models when no
    query is provided.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    
    expected_models = [MockModel(id=1), MockModel(id=2)]
    mock_query.all.return_value = expected_models
    
    results = repository.find_all()
    
    # Verify query operations
    mock_session.query.assert_called_once_with(MockModel)
    mock_query.all.assert_called_once()
    mock_session.close.assert_called_once()
    
    assert results == expected_models


def test_find_all_with_query(repository, mock_sqlalchemy_components):
    """
    Test finding models with specific query criteria.

    This test verifies that find_all correctly applies filter_by
    criteria and returns matching models.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    
    expected_models = [MockModel(id=1, name="Alice")]
    mock_query.all.return_value = expected_models
    
    query = {"name": "Alice"}
    results = repository.find_all(query)
    
    # Verify query operations
    mock_query.filter_by.assert_called_once_with(**query)
    assert results == expected_models


def test_find_all_with_pagination(repository, mock_sqlalchemy_components):
    """
    Test finding models with skip and limit parameters.

    This test verifies that find_all correctly applies offset and limit
    to the query for pagination support.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []
    
    repository.find_all(query={"active": True}, skip=10, limit=5)
    
    # Verify pagination was applied
    mock_query.offset.assert_called_once_with(10)
    mock_query.limit.assert_called_once_with(5)


def test_find_all_exception(repository, mock_sqlalchemy_components):
    """
    Test find_all when an exception occurs during query.

    This test verifies that find_all returns an empty list and handles
    exceptions gracefully during query execution.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_session.query.side_effect = Exception("Database error")
    
    with patch('builtins.print') as mock_print:
        results = repository.find_all({"name": "Test"})
        
        assert results == []
        mock_session.close.assert_called_once()
        mock_print.assert_called_once()
        assert "SQLAlchemy find_all error" in mock_print.call_args[0][0]


def test_update_success(repository, mock_sqlalchemy_components):
    """
    Test successful model update in SQLAlchemy.

    This test verifies that update correctly retrieves a model, applies
    changes, commits the transaction, and returns the updated model.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    
    # Mock the model to be updated
    mock_instance = MockModel(id=1, name="Original", value=50)
    mock_query.get.return_value = mock_instance
    
    update_data = {"name": "Updated", "value": 100}
    result = repository.update(1, update_data)
    
    # Verify the attributes were updated
    assert mock_instance.name == "Updated"
    assert mock_instance.value == 100
    
    # Verify session operations
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_instance)
    mock_session.close.assert_called_once()
    
    assert result == mock_instance


def test_update_not_found(repository, mock_sqlalchemy_components):
    """
    Test updating a non-existent model.

    This test verifies that update returns None when no model
    matches the provided ID.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.get.return_value = None
    
    result = repository.update(999, {"name": "Updated"})
    
    assert result is None
    mock_session.close.assert_called_once()


def test_update_integrity_error(repository, mock_sqlalchemy_components):
    """
    Test handling of integrity errors during update.

    This test verifies that update returns None when an IntegrityError
    occurs during the update operation.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    
    mock_instance = MockModel(id=1, name="Original")
    mock_query.get.return_value = mock_instance
    mock_session.commit.side_effect = IntegrityError("statement", "params", "orig")
    
    with patch('builtins.print') as mock_print:
        result = repository.update(1, {"name": "Duplicate"})
        
        assert result is None
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_print.assert_called_once()
        assert "SQLAlchemy update error" in mock_print.call_args[0][0]


def test_delete_success(repository, mock_sqlalchemy_components):
    """
    Test successful model deletion from SQLAlchemy.

    This test verifies that delete correctly retrieves and removes
    a model from the database.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    
    mock_instance = MockModel(id=1, name="ToDelete")
    mock_query.get.return_value = mock_instance
    
    result = repository.delete(1)
    
    # Verify session operations
    mock_session.delete.assert_called_once_with(mock_instance)
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()
    
    assert result is True


def test_delete_not_found(repository, mock_sqlalchemy_components):
    """
    Test deleting a non-existent model.

    This test verifies that delete returns False when no model
    matches the provided ID.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.get.return_value = None
    
    result = repository.delete(999)
    
    assert result is False
    mock_session.close.assert_called_once()


def test_count_all_models(repository, mock_sqlalchemy_components):
    """
    Test counting all models in the database.

    This test verifies that count returns the correct total number
    of models when no query is provided.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.count.return_value = 42
    
    result = repository.count()
    
    # Verify query operations
    mock_session.query.assert_called_once_with(MockModel)
    mock_query.count.assert_called_once()
    mock_session.close.assert_called_once()
    
    assert result == 42


def test_count_with_query(repository, mock_sqlalchemy_components):
    """
    Test counting models that match query criteria.

    This test verifies that count correctly applies filter_by
    criteria and returns the count of matching models.
    """
    mock_session = mock_sqlalchemy_components['session']
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.count.return_value = 15
    
    query = {"active": True}
    result = repository.count(query)
    
    # Verify query operations
    mock_query.filter_by.assert_called_once_with(**query)
    mock_query.count.assert_called_once()
    
    assert result == 15


def test_session_management_in_all_methods(repository, mock_sqlalchemy_components):
    """
    Test that all methods properly manage sessions (create and close).

    This test verifies that every repository method creates a session
    and ensures it's closed, even when exceptions occur.
    """
    mock_session = mock_sqlalchemy_components['session']
    
    # Test that each method creates and closes a session
    methods_to_test = [
        lambda: repository.get_by_id(1),
        lambda: repository.find_one({"name": "test"}),
        lambda: repository.find_all(),
        lambda: repository.update(1, {"name": "updated"}),
        lambda: repository.delete(1),
        lambda: repository.count()
    ]
    
    for method in methods_to_test:
        mock_session.reset_mock()
        mock_sqlalchemy_components['session_class'].reset_mock()
        
        # Set up minimal mocks to avoid errors
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.get.return_value = None
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_query.count.return_value = 0
        
        method()
        
        # Verify session was created and closed
        mock_sqlalchemy_components['session_class'].assert_called_once()
        mock_session.close.assert_called_once()

