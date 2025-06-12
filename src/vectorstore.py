# def store_embeddings(embeddings: List, metadatas: List[dict], index_name: str): ...
# def search_similar_chunks(query: str, index_name: str) -> List[str]: ...
# def init_vector_store(): ...

from langchain_milvus import Milvus
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore

def setup_vector_store(embeddings):
    # Vector Store
    vector_store = Milvus(
        embedding_function=embeddings,
        index_params={"index_type":"HNSW", "metric_type": "L2"},
        connection_args={
            "host": "localhost",
            "port": "19530"
            },
        collection_name="ISRO_Report_2025"
        )

    # Docstore
    docstore = InMemoryStore()

    # Key
    id_key = "doc_id"

    return vector_store, docstore, id_key

def multi_vector_retriever(vector_store, docstore, id_key):
    retriever = MultiVectorRetriever(
        vectorstore=vector_store,
        docstore=docstore,
        id_key=id_key,
    )
    return retriever