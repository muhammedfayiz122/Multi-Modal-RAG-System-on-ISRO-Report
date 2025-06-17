# def store_embeddings(embeddings: List, metadatas: List[dict], index_name: str): ...
# def search_similar_chunks(query: str, index_name: str) -> List[str]: ...
# def init_vector_store(): ...

from langchain_milvus import Milvus
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain.storage.redis import RedisStore
from embedder import load_embedding_model, generate_embedding_model

docstore = RedisStore(redis_url="redis://localhost:379")
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

def add_documents(retriever, doc, ids, raw_data):
    retriever.vectorstore.add_documents(doc)
    retriever.docstore.mset(list(zip(ids, raw_data)))

def add_documents(retriever, vectorstore_doc, docstore_doc):
    retriever.vectorstore.add_documents(vectorstore_doc)
    retriever.docstore.mset({})
# def add_images(retriever, image_doc, img_base64_list, image_ids):
#     retriever.vectorstore.add_documents(image_doc)
#     retriever.docstore.mset(list(zip(image_ids, img_base64_list)))