# def store_embeddings(embeddings: List, metadatas: List[dict], index_name: str): ...
# def search_similar_chunks(query: str, index_name: str) -> List[str]: ...
# def init_vector_store(): ...

from langchain_milvus import Milvus
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_community.storage import RedisStore
from utils.mongodb_docstore import MongoDBDocStore
from langchain.storage import InMemoryStore
from utils.save_load_files import reload_json
from utils.logger import logging
from embedder import load_embedding_model


docstore = MongoDBDocStore()
embedding_model = load_embedding_model()

def setup_vector_store():
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

def multi_vector_retriever(vector_store):
    retriever = MultiVectorRetriever(
        vectorstore=vector_store,
        docstore=MongoDBDocStore(),
        id_key="doc_id",
    )
    return retriever

def add_documents(retriever, summary_docs, raw_docs, ):
    """
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

def get_retriever():
    vector_store = setup_vector_store()
    retriever = multi_vector_retriever(vector_store=vector_store)
    return retriever





# def add_images(retriever, image_doc, img_base64_list, image_ids):
#     retriever.vectorstore.add_documents(image_doc)
#     retriever.docstore.mset(list(zip(image_ids, img_base64_list)))