from typing import List, Tuple, Optional, Iterable
from pymongo import MongoClient
from langchain_core.documents import Document
from langchain_core.stores import BaseStore


class MongoDBDocStore(BaseStore[str, Document]):
    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "docstore_db",
        collection_name: str = "documents"
    ):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def mset(self, items: List[Tuple[str, Document]]) -> None:
        for doc_id, doc in items:
            doc_dict = {
                "_id": doc_id,
                "page_content": doc.page_content,
                "metadata": doc.metadata
            }
            self.collection.replace_one({"_id": doc_id}, doc_dict, upsert=True)

    def mget(self, keys: List[str]) -> List[Optional[Document]]:
        docs = self.collection.find({"_id": {"$in": keys}})
        id_to_doc = {
            doc["_id"]: Document(page_content=doc["page_content"], metadata=doc["metadata"])
            for doc in docs
        }
        return [id_to_doc.get(key) for key in keys]

    def yield_keys(self) -> Iterable[str]:
        return (doc["_id"] for doc in self.collection.find({}, {"_id": 1}))
    
    def mdelete(self, keys: List[str]) -> None:
        self.collection.delete_many({"_id": {"$in": keys}})

