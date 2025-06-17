from unstructured.chunking.title import chunk_by_title
from pdf_loader import text_to_documents, summarize_texts
from utils.save_load_files import reload_json
from utils.extract_utils import elements_wise_extractor
from utils.logger import logging
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from utils.save_load_files import reload, save_as_pickle

def make_chunks(pdf_elements):  
    """
    chunk the texts further by the title
    """
    chunked_elements = chunk_by_title(pdf_elements)
    return chunked_elements 

def text_chunker(pdf_elements):
    """
    """
    chunked_elements = make_chunks(pdf_elements)
    texts, text_elements, _, _ = elements_wise_extractor(chunked_elements, "CompositeElement")
    summaries = reload_json("summaries/text_summaries.json", summarize_texts, texts)
    doc_for_vectorstore, doc_for_docstore = text_to_documents(text_elements, texts, summaries)
    return doc_for_vectorstore, doc_for_docstore


# def chunk_text(text_blocks: List[str], max_length: int = 500) -> List[str]: ...
# def chunk_tables(tables: List[pd.DataFrame]) -> List[str]: ...
# def chunk_image_captions(captions: Dict[str, str]) -> List[str]: ...
