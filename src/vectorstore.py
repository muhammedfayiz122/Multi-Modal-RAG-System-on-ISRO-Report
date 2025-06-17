# def store_embeddings(embeddings: List, metadatas: List[dict], index_name: str): ...
# def search_similar_chunks(query: str, index_name: str) -> List[str]: ...
# def init_vector_store(): ...

from langchain_milvus import Milvus
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain.storage.redis import RedisStore
from utils.save_load_files import reload_json
from utils.logger import logging
from embedder import load_embedding_model, generate_embedding_model

docstore = RedisStore(redis_url="redis://localhost:6379")
embedding_model = load_embedding_model()

def setup_vector_store(embedding_model):
    # Vector Store
    vector_store = Milvus(
        embedding_function=embedding_model.encode,
        index_params={
            "index_type":"IVF_FLAT", 
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        },
        connection_args={
            "host": "localhost",
            "port": "19530",
        },
        collection_name="ISRO_Report_2025"
    )
    return vector_store

def multi_vector_retriever(vector_store):
    retriever = MultiVectorRetriever(
        vectorstore=vector_store,
        docstore=docstore,
        id_key="doc_id",
    )
    return retriever

def add_documents(retriever, summary_docs, raw_docs, ):
    """
    """
    existing_ids = list(retriever.docstore.yield_keys())
    ids = [doc.metadata["doc_id"] for doc in summary_docs] # Milvus needs ids to be passed separately
    for id in ids:
        if id in existing_ids:
            print("Error : trying to add existing id")
            logging.info("Error : trying to add existing id")
            return
    doc_type = summary_docs[0].metadata["type"] 
    vectors = reload_json(f"vectors/{doc_type}_vectors.json", generate_embedding_model, embedding_model, summary_docs)
    logging.info(f"Generated {doc_type} vectors")
   

    # Add vectorized summary documents
    retriever.vectorstore.add_vectors(
        vectors=vectors,
        documents=summary_docs,
        ids=ids
    )

    # Add documnets in DocStore
    retriever.docstore.mset(list(zip(ids, raw_docs)))
    logging.info(f"Adding {doc_type} documents completed")

def get_retriever():
    vector_store = setup_vector_store(embedding_model=embedding_model)
    retriever = multi_vector_retriever(vector_store=vector_store)
    return retriever





# def add_images(retriever, image_doc, img_base64_list, image_ids):
#     retriever.vectorstore.add_documents(image_doc)
#     retriever.docstore.mset(list(zip(image_ids, img_base64_list)))