from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from typing import Dict, Any, List, Optional, Type, TypeVar
import os

from ._model_repository import ModelRepository


T = TypeVar("T")


class MongoDBModelRepository(ModelRepository[T]):
    """
    MongoDB implementation of the ModelRepository interface.

    This class provides CRUD operations for MongoDB collections, with support
    for wrapping database documents in model classes for easier access.

    Attributes:
        client: The MongoDB client connection
        db: The MongoDB database instance
        collection: The MongoDB collection being managed
        model_class: Class used to wrap raw MongoDB documents
    """

    def __init__(self, db_uri: str, db_name: str, model_class: Type[T]):
        """
        Initialize a MongoDB model manager.

        Args:
            db_uri: URI connection string for database
            db_name: Name of the MongoDB database
            model_class: Class to wrap returned documents (provides object-oriented access)
        """
        super().__init__(model_class)

        collection_name = model_class.__name__

        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def _wrap_result(self, data: Optional[Dict[str, Any]]) -> Optional[T]:
        """
        Wrap a MongoDB document in the model wrapper class.

        Args:
            data: Raw MongoDB document dictionary

        Returns:
            An instance of the model wrapper class or None if data is None
        """
        if data:
            return self.model_class(**data)
        return None

    def create(self, model_data: Dict[str, Any]) -> Optional[T]:
        """
        Create a new document in the MongoDB collection.

        Args:
            model_data: Dictionary containing the document data

        Returns:
            The created model instance or None if creation fails (e.g., due to duplicate key)

        Note:
            The returned model includes the MongoDB-generated _id field
        """
        try:
            result = self.collection.insert_one(model_data)
            # MongoDB returns _id as ObjectId, ensure it's in the returned dict
            model_data["_id"] = result.inserted_id
            return self._wrap_result(model_data)
        except DuplicateKeyError as e:
            print(f"MongoDB create error: {e}")
            return None

    def get_by_id(self, model_id: Any) -> Optional[T]:
        """
        Retrieve a document by its MongoDB _id.

        Args:
            model_id: The document's _id (can be string or ObjectId)

        Returns:
            The model instance or None if not found or if the ID format is invalid
        """
        if not isinstance(model_id, ObjectId):
            try:
                model_id = ObjectId(model_id)
            except Exception:
                return None  # Invalid ObjectId format

        result = self.collection.find_one({"_id": model_id})
        return self._wrap_result(result)

    def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """
        Find a single document matching the query criteria.

        Args:
            query: MongoDB query dictionary

        Returns:
            The first matching model instance or None if no matches found
        """
        result = self.collection.find_one(query)
        return self._wrap_result(result)

    def find_all(
        self,
        query: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[T]:
        """
        Find all documents matching the query criteria with optional pagination.

        Args:
            query: MongoDB query dictionary (defaults to empty query which matches all documents)
            limit: Maximum number of results to return
            skip: Number of results to skip (for pagination)

        Returns:
            A list of model instances matching the query
        """
        query = query if query is not None else {}
        cursor = self.collection.find(query)
        if skip is not None:
            cursor = cursor.skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
        results = [self._wrap_result(doc) for doc in cursor]
        return [r for r in results if r is not None]

    def update(self, model_id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing document by its _id.

        Args:
            model_id: The document's _id (can be string or ObjectId)
            update_data: Dictionary containing the fields to update and their new values

        Returns:
            The updated model instance or None if not found/updated or if the ID format is invalid

        Note:
            Uses MongoDB's $set operator to update only the specified fields
        """
        if not isinstance(model_id, ObjectId):
            try:
                model_id = ObjectId(model_id)
            except Exception:
                return None

        try:
            result = self.collection.update_one(
                {"_id": model_id}, {"$set": update_data}
            )
            if result.matched_count > 0:
                return self.get_by_id(model_id)  # Fetch the updated document
            return None
        except DuplicateKeyError as e:
            print(f"MongoDB update error: {e}")
            return None

    def delete(self, model_id: Any) -> bool:
        """
        Delete a document by its _id.

        Args:
            model_id: The document's _id (can be string or ObjectId)

        Returns:
            True if the document was deleted, False otherwise or if the ID format is invalid
        """
        if not isinstance(model_id, ObjectId):
            try:
                model_id = ObjectId(model_id)
            except Exception:
                return False

        result = self.collection.delete_one({"_id": model_id})
        return result.deleted_count > 0

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count the number of documents matching a query.

        Args:
            query: MongoDB query dictionary (defaults to empty query which matches all documents)

        Returns:
            The number of matching documents
        """
        query = query if query is not None else {}
        return self.collection.count_documents(query)
