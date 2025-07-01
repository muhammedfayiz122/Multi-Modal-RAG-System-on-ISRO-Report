from typing import List
from langchain_core.documents import Document
from langchain_milvus import Milvus
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_community.storage import RedisStore
from utils.mongodb_docstore import MongoDBDocStore
from utils.save_load_files import reload_json
from utils.logger import logging
from embedder import load_embedding_model

"""
vectorstore.py

This module handles setup and operations for vector storage and retrieval using:
- Milvus as the vector database
- MongoDB as the document store
- MultiVectorRetriever from Langchain to enable hybrid RAG

Supports storing text, table, and image embeddings separately and avoiding duplicates.
"""

docstore = MongoDBDocStore()
embedding_model = load_embedding_model()

def setup_vector_store() -> Milvus:
    """
    Initializes and configures a Milvus vector store.

    Returns:
        Milvus: Langchain-compatible Milvus vector store.
    """
    # Vector Store
    vector_store = Milvus(
        embedding_function=embedding_model,
        index_params={
            "index_type":"IVF_FLAT", 
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        },
        connection_args={
            "host": "milvus",
            "port": "19530",
        },
        collection_name="ISRO_Report_2025"
    )
    return vector_store

def multi_vector_retriever(vector_store: Milvus) -> MultiVectorRetriever:
    """
    Builds a MultiVectorRetriever using Milvus and MongoDB.

    Args:
        vector_store (Milvus): Milvus instance for semantic search.

    Returns:
        MultiVectorRetriever: Langchain retriever combining vector and docstore.
    """
    retriever = MultiVectorRetriever(
        vectorstore=vector_store,
        docstore=MongoDBDocStore(),
        id_key="doc_id",
    )
    return retriever

def add_documents(retriever: MultiVectorRetriever, summary_docs: List[Document], raw_docs: List[Document]) -> None:
    """
    Adds summary (vector) + raw (docstore) documents to the retriever.

    Skips already existing `doc_id`s to prevent duplication.

    Args:
        retriever (MultiVectorRetriever): Configured retriever instance.
        summary_docs (List[Document]): Summarized/embedded documents for semantic retrieval.
        raw_docs (List[Document]): Full documents for final display.

    Raises:
        ValueError: If lengths of summary_docs and raw_docs do not match.
    """
    existing_ids = list(retriever.docstore.yield_keys())
    ids = [doc.metadata["doc_id"] for doc in summary_docs] # Milvus needs ids to be passed separately
    doc_type = summary_docs[0].metadata["type"]
    for id in ids:
        if id in existing_ids:
            print(f"existing id found, skipping {doc_type}")
            logging.info("Error : trying to add existing id ")
            return
    doc_type = summary_docs[0].metadata["type"] 
    logging.info(f"Adding {doc_type} documents...")
   
    # Add vectorized summary documents
    retriever.vectorstore.add_documents(
        documents=summary_docs,
        ids=ids
    )

    # Add raw documents in DocStore
    retriever.docstore.mset(list(zip(ids, raw_docs)))
    logging.info(f"Adding {doc_type} documents successfully")

def get_retriever() -> MultiVectorRetriever:
    """
    Returns a retriever with pre-configured Milvus + MongoDB.

    Returns:
        MultiVectorRetriever: Langchain retriever instance.
    """
    vector_store = setup_vector_store()
    retriever = multi_vector_retriever(vector_store=vector_store)
    return retriever
