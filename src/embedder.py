from langchain_huggingface import HuggingFaceEmbeddings
from utils.logger import logging
import time

def load_embedding_model():
    start_time = time.time()
    print("Loading HuggingFace embedding model...")
    embedding = HuggingFaceEmbeddings(
        model_name="intfloat/e5-base-v2",
        encode_kwargs={
            'normalize_embeddings': True,
            'show_progress_bar': True,
            'convert_to_tensor': True
            }  # important for E5 models
        
    )
    end_time = time.time()
    logging.info(f"Embedding model loaded in {end_time - start_time:.2f} seconds.")
    return embedding

# Hugging Face embedding models :  
# e5-large-v2
# intfloat/e5-base-v2
# intfloat/e5-small-v2
# bge-base-en
# all-MiniLM-L6-v2


# def get_text_embedding(text: str) -> List[float]: ...
# def get_image_embedding(image_path: str) -> List[float]: ...
# def load_embedding_model(model_name: str):
    
