"""
Fallback in-memory database for development when MongoDB Atlas is not accessible
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class FallbackDatabase:
    def __init__(self):
        self.collections = {}

    def get_collection(self, name: str):
        if name not in self.collections:
            self.collections[name] = FallbackCollection(name)
        return self.collections[name]

class FallbackCollection:
    def __init__(self, name: str):
        self.name = name
        self.documents = []

    async def insert_one(self, document: Dict[str, Any]):
        # Add _id if not present
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())

        self.documents.append(document.copy())

        # Return result similar to MongoDB
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id

        return InsertResult(document["_id"])

    async def find_one(self, filter_dict: Dict[str, Any]):
        for doc in self.documents:
            if self._matches_filter(doc, filter_dict):
                return doc.copy()
        return None

    async def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        for i, doc in enumerate(self.documents):
            if self._matches_filter(doc, filter_dict):
                # Handle $set operations
                if "$set" in update_dict:
                    doc.update(update_dict["$set"])
                else:
                    doc.update(update_dict)

                class UpdateResult:
                    def __init__(self, matched_count):
                        self.matched_count = matched_count

                return UpdateResult(1)

        class UpdateResult:
            def __init__(self, matched_count):
                self.matched_count = matched_count

        return UpdateResult(0)

    async def delete_one(self, filter_dict: Dict[str, Any]):
        for i, doc in enumerate(self.documents):
            if self._matches_filter(doc, filter_dict):
                del self.documents[i]

                class DeleteResult:
                    def __init__(self, deleted_count):
                        self.deleted_count = deleted_count

                return DeleteResult(1)

        class DeleteResult:
            def __init__(self, deleted_count):
                self.deleted_count = deleted_count

        return DeleteResult(0)

    def _matches_filter(self, document: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        for key, value in filter_dict.items():
            if key not in document or document[key] != value:
                return False
        return True

# Global fallback database instance
fallback_db = FallbackDatabase()

class FallbackAdmin:
    async def command(self, command_name: str):
        if command_name == 'ping':
            return {"ok": 1.0}
        return {"ok": 1.0}

class FallbackClient:
    def __init__(self):
        self.carbonchain = fallback_db
        self.admin = FallbackAdmin()

    def close(self):
        pass