from unstructured.chunking.title import chunk_by_title
from pdf_loader import elements_extractor
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from utils.save_load_files import reload, save_as_pickle

def make_chunks(pdf_elements):
    """
    chunk the texts further by the title
    """
    chunked_elements = chunk_by_title(pdf_elements)
    return chunked_elements 

def chunker(pdf_elements):
    """
    """
    chunked_elements = make_chunks(pdf_elements)
    extracted_chunks = elements_extractor(chunked_elements)
    texts = extracted_chunks["CompositeElements"]
    # save_as_pickle(texts, "chunked_texts.pkl")
    return texts
