"""
Tests for the MongoDBModelRepository class in the modelrepo.repository._mongo_db_model_repository module.

This module tests the MongoDB implementation of the ModelRepository interface,
ensuring all CRUD operations work correctly with MongoDB-specific features like
ObjectId handling and document wrapping. The tests use mocking to avoid requiring
a real MongoDB connection.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

from modelrepo.repository._mongo_db_model_repository import MongoDBModelRepository


class MockModel:
    """Mock model class for testing MongoDB operations."""

    def __init__(self, _id: str = None, name: str = "test", value: int = 0, **kwargs):
        self._id = _id
        self.name = name
        self.value = value
        # Store any additional kwargs as attributes
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __eq__(self, other):
        if not isinstance(other, MockModel):
            return False
        return (
            self._id == other._id
            and self.name == other.name
            and self.value == other.value
        )


@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoDB client for testing."""
    with patch(
        "modelrepo.repository._mongo_db_model_repository.MongoClient"
    ) as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Set up the database and collection mocks
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        yield {
            "client": mock_client,
            "instance": mock_instance,
            "db": mock_db,
            "collection": mock_collection,
        }


@pytest.fixture
def repository(mock_mongo_client):
    """Create a MongoDBModelRepository instance for testing."""
    return MongoDBModelRepository("mongodb://test", "test_db", MockModel)


def test_repository_initialization(mock_mongo_client):
    """
    Test that MongoDBModelRepository initializes correctly with MongoDB connection.

    This test verifies that the repository properly connects to MongoDB,
    sets up the database and collection references, and stores the model class.
    """
    repo = MongoDBModelRepository(
        "mongodb://localhost:27017", "test_database", MockModel
    )

    # Verify MongoDB client was created with correct URI
    mock_mongo_client["client"].assert_called_once_with("mongodb://localhost:27017")

    # Verify the repository has correct attributes
    assert repo.model_class == MockModel
    assert repo.client == mock_mongo_client["instance"]
    assert repo.db == mock_mongo_client["db"]
    assert repo.collection == mock_mongo_client["collection"]


def test_collection_name_from_model_class(mock_mongo_client):
    """
    Test that collection name is derived from model class name.

    This test verifies that the repository uses the model class name
    as the MongoDB collection name.
    """

    class CustomModel:
        pass

    MongoDBModelRepository("mongodb://test", "test_db", CustomModel)

    # The collection should be accessed with the class name
    mock_mongo_client["db"].__getitem__.assert_called_with("CustomModel")


def test_wrap_result_with_data(repository):
    """
    Test wrapping MongoDB document data into model instances.

    This test verifies that _wrap_result correctly creates model instances
    from MongoDB document dictionaries.
    """
    test_data = {"_id": ObjectId(), "name": "Test", "value": 42}

    result = repository._wrap_result(test_data)

    assert isinstance(result, MockModel)
    assert result._id == test_data["_id"]
    assert result.name == "Test"
    assert result.value == 42


def test_wrap_result_with_none(repository):
    """
    Test wrapping None data returns None.

    This test verifies that _wrap_result returns None when given None input,
    which happens when MongoDB queries return no results.
    """
    result = repository._wrap_result(None)

    assert result is None


def test_create_success(repository, mock_mongo_client):
    """
    Test successful document creation in MongoDB.

    This test verifies that create properly inserts documents into MongoDB
    and returns the created model with the generated ObjectId.
    """
    mock_collection = mock_mongo_client["collection"]
    mock_result = Mock()
    mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439011")
    mock_collection.insert_one.return_value = mock_result

    model_data = {"name": "Test User", "value": 100}
    result = repository.create(model_data)

    # Verify insert_one was called with correct data
    mock_collection.insert_one.assert_called_once_with(model_data)

    # Verify the result includes the inserted ID
    assert isinstance(result, MockModel)
    assert result._id == mock_result.inserted_id
    assert result.name == "Test User"
    assert result.value == 100


def test_create_duplicate_key_error(repository, mock_mongo_client):
    """
    Test handling of duplicate key errors during creation.

    This test verifies that create returns None when a DuplicateKeyError
    occurs, indicating a constraint violation (e.g., unique index).
    """
    mock_collection = mock_mongo_client["collection"]
    mock_collection.insert_one.side_effect = DuplicateKeyError("Duplicate key error")

    with patch("builtins.print") as mock_print:
        result = repository.create({"name": "Duplicate"})

        assert result is None
        mock_print.assert_called_once()
        assert "MongoDB create error" in mock_print.call_args[0][0]


def test_get_by_id_with_object_id(repository, mock_mongo_client):
    """
    Test retrieving a document by ObjectId.

    This test verifies that get_by_id correctly handles ObjectId parameters
    and returns the wrapped model when a document is found.
    """
    mock_collection = mock_mongo_client["collection"]
    test_id = ObjectId("507f1f77bcf86cd799439011")
    test_doc = {"_id": test_id, "name": "Found", "value": 50}
    mock_collection.find_one.return_value = test_doc

    result = repository.get_by_id(test_id)

    mock_collection.find_one.assert_called_once_with({"_id": test_id})
    assert isinstance(result, MockModel)
    assert result._id == test_id
    assert result.name == "Found"


def test_get_by_id_with_string_id(repository, mock_mongo_client):
    """
    Test retrieving a document by string ID that gets converted to ObjectId.

    This test verifies that get_by_id automatically converts string IDs
    to ObjectId instances for MongoDB queries.
    """
    mock_collection = mock_mongo_client["collection"]
    test_id_str = "507f1f77bcf86cd799439011"
    test_id_obj = ObjectId(test_id_str)
    test_doc = {"_id": test_id_obj, "name": "Found", "value": 50}
    mock_collection.find_one.return_value = test_doc

    result = repository.get_by_id(test_id_str)

    mock_collection.find_one.assert_called_once_with({"_id": test_id_obj})
    assert isinstance(result, MockModel)
    assert result._id == test_id_obj


def test_get_by_id_invalid_object_id(repository, mock_mongo_client):
    """
    Test handling of invalid ObjectId strings.

    This test verifies that get_by_id returns None when given an invalid
    ObjectId string that cannot be converted.
    """
    result = repository.get_by_id("invalid_object_id")

    assert result is None
    # Should not call find_one with invalid ID
    mock_mongo_client["collection"].find_one.assert_not_called()


def test_get_by_id_not_found(repository, mock_mongo_client):
    """
    Test retrieving a non-existent document.

    This test verifies that get_by_id returns None when no document
    matches the provided ID.
    """
    mock_collection = mock_mongo_client["collection"]
    mock_collection.find_one.return_value = None

    test_id = ObjectId("507f1f77bcf86cd799439011")
    result = repository.get_by_id(test_id)

    assert result is None


def test_find_one_success(repository, mock_mongo_client):
    """
    Test finding a single document with query criteria.

    This test verifies that find_one correctly passes query parameters
    to MongoDB and returns the wrapped result.
    """
    mock_collection = mock_mongo_client["collection"]
    test_doc = {"_id": ObjectId(), "name": "Alice", "value": 100}
    mock_collection.find_one.return_value = test_doc

    query = {"name": "Alice"}
    result = repository.find_one(query)

    mock_collection.find_one.assert_called_once_with(query)
    assert isinstance(result, MockModel)
    assert result.name == "Alice"


def test_find_one_not_found(repository, mock_mongo_client):
    """
    Test find_one when no documents match the query.

    This test verifies that find_one returns None when no documents
    match the provided query criteria.
    """
    mock_collection = mock_mongo_client["collection"]
    mock_collection.find_one.return_value = None

    result = repository.find_one({"name": "NonExistent"})

    assert result is None


def test_find_all_no_query(repository, mock_mongo_client):
    """
    Test finding all documents without query criteria.

    This test verifies that find_all returns all documents when no
    query is provided, using an empty query dictionary.
    """
    mock_collection = mock_mongo_client["collection"]
    test_docs = [
        {"_id": ObjectId(), "name": "Alice", "value": 100},
        {"_id": ObjectId(), "name": "Bob", "value": 200},
    ]
    mock_cursor = MagicMock()
    mock_cursor.__iter__.return_value = test_docs
    mock_collection.find.return_value = mock_cursor

    results = repository.find_all()

    mock_collection.find.assert_called_once_with({})
    assert len(results) == 2
    assert all(isinstance(r, MockModel) for r in results)


def test_find_all_with_query(repository, mock_mongo_client):
    """
    Test finding documents with specific query criteria.

    This test verifies that find_all correctly applies query filters
    and returns only matching documents.
    """
    mock_collection = mock_mongo_client["collection"]
    mock_cursor = MagicMock()
    test_docs = [{"_id": ObjectId(), "name": "Alice", "value": 100}]
    mock_cursor.__iter__.return_value = test_docs
    mock_collection.find.return_value = mock_cursor

    query = {"value": 100}
    results = repository.find_all(query)

    mock_collection.find.assert_called_once_with(query)
    assert len(results) == 1


def test_find_all_with_pagination(repository, mock_mongo_client):
    """
    Test finding documents with skip and limit parameters.

    This test verifies that find_all correctly applies pagination
    parameters to the MongoDB cursor.
    """
    mock_collection = mock_mongo_client["collection"]
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_collection.find.return_value = mock_cursor

    repository.find_all(query={"active": True}, skip=10, limit=5)

    mock_cursor.skip.assert_called_once_with(10)
    mock_cursor.limit.assert_called_once_with(5)


def test_update_success(repository, mock_mongo_client):
    """
    Test successful document update in MongoDB.

    This test verifies that update correctly applies changes to a document
    and returns the updated model instance.
    """
    mock_collection = mock_mongo_client["collection"]
    test_id = ObjectId("507f1f77bcf86cd799439011")

    # Mock successful update
    mock_result = Mock()
    mock_result.matched_count = 1
    mock_collection.update_one.return_value = mock_result

    # Mock the get_by_id call that happens after update
    updated_doc = {"_id": test_id, "name": "Updated", "value": 999}
    mock_collection.find_one.return_value = updated_doc

    update_data = {"name": "Updated", "value": 999}
    result = repository.update(test_id, update_data)

    # Verify update_one was called with correct parameters
    mock_collection.update_one.assert_called_once_with(
        {"_id": test_id}, {"$set": update_data}
    )

    # Verify the updated document was fetched and wrapped
    assert isinstance(result, MockModel)
    assert result.name == "Updated"
    assert result.value == 999


def test_update_not_found(repository, mock_mongo_client):
    """
    Test updating a non-existent document.

    This test verifies that update returns None when no document
    matches the provided ID.
    """
    mock_collection = mock_mongo_client["collection"]
    test_id = ObjectId("507f1f77bcf86cd799439011")

    # Mock no documents matched
    mock_result = Mock()
    mock_result.matched_count = 0
    mock_collection.update_one.return_value = mock_result

    result = repository.update(test_id, {"name": "Updated"})

    assert result is None


def test_update_invalid_object_id(repository, mock_mongo_client):
    """
    Test updating with an invalid ObjectId.

    This test verifies that update returns None when given an invalid
    ObjectId string that cannot be converted.
    """
    result = repository.update("invalid_id", {"name": "Updated"})

    assert result is None
    # Should not call update_one with invalid ID
    mock_mongo_client["collection"].update_one.assert_not_called()


def test_update_duplicate_key_error(repository, mock_mongo_client):
    """
    Test handling of duplicate key errors during update.

    This test verifies that update returns None when a DuplicateKeyError
    occurs during the update operation.
    """
    mock_collection = mock_mongo_client["collection"]
    mock_collection.update_one.side_effect = DuplicateKeyError("Duplicate key error")

    test_id = ObjectId("507f1f77bcf86cd799439011")

    with patch("builtins.print") as mock_print:
        result = repository.update(test_id, {"name": "Duplicate"})

        assert result is None
        mock_print.assert_called_once()
        assert "MongoDB update error" in mock_print.call_args[0][0]


def test_delete_success(repository, mock_mongo_client):
    """
    Test successful document deletion from MongoDB.

    This test verifies that delete correctly removes a document
    and returns True when the operation succeeds.
    """
    mock_collection = mock_mongo_client["collection"]
    test_id = ObjectId("507f1f77bcf86cd799439011")

    # Mock successful deletion
    mock_result = Mock()
    mock_result.deleted_count = 1
    mock_collection.delete_one.return_value = mock_result

    result = repository.delete(test_id)

    mock_collection.delete_one.assert_called_once_with({"_id": test_id})
    assert result is True


def test_delete_not_found(repository, mock_mongo_client):
    """
    Test deleting a non-existent document.

    This test verifies that delete returns False when no document
    matches the provided ID.
    """
    mock_collection = mock_mongo_client["collection"]
    test_id = ObjectId("507f1f77bcf86cd799439011")

    # Mock no documents deleted
    mock_result = Mock()
    mock_result.deleted_count = 0
    mock_collection.delete_one.return_value = mock_result

    result = repository.delete(test_id)

    assert result is False


def test_delete_invalid_object_id(repository, mock_mongo_client):
    """
    Test deleting with an invalid ObjectId.

    This test verifies that delete returns False when given an invalid
    ObjectId string that cannot be converted.
    """
    result = repository.delete("invalid_id")

    assert result is False
    # Should not call delete_one with invalid ID
    mock_mongo_client["collection"].delete_one.assert_not_called()


def test_count_all_documents(repository, mock_mongo_client):
    """
    Test counting all documents in the collection.

    This test verifies that count returns the correct total number
    of documents when no query is provided.
    """
    mock_collection = mock_mongo_client["collection"]
    mock_collection.count_documents.return_value = 42

    result = repository.count()

    mock_collection.count_documents.assert_called_once_with({})
    assert result == 42


def test_count_with_query(repository, mock_mongo_client):
    """
    Test counting documents that match query criteria.

    This test verifies that count correctly applies query filters
    and returns the count of matching documents.
    """
    mock_collection = mock_mongo_client["collection"]
    mock_collection.count_documents.return_value = 15

    query = {"active": True}
    result = repository.count(query)

    mock_collection.count_documents.assert_called_once_with(query)
    assert result == 15
