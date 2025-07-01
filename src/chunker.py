from unstructured.chunking.title import chunk_by_title
from pdf_loader import text_to_documents, summarize_texts
from utils.save_load_files import reload_json
from utils.extract_utils import elements_wise_extractor
from utils.logger import logging
from typing import List
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from utils.save_load_files import reload, save_as_pickle

"""
chunker.py

This module handles chunking of the extracted PDF content, particularly text.
It uses `unstructured` to split by titles and prepares the content for summarization and vectorization.
"""

def make_chunks(pdf_elements: List) -> List:  
    """
    Chunk the raw PDF elements based on section titles.

    Args:
        pdf_elements (List[Element]): Elements extracted from the PDF.

    Returns:
        List[Element]: Chunks grouped logically based on document titles.
    """
    chunked_elements = chunk_by_title(pdf_elements)
    return chunked_elements 

def text_chunker(pdf_elements):
    """
    Full pipeline to:
    1. Chunk text by title
    2. Extract only relevant text elements
    3. Generate summaries
    4. Convert to vectorstore and docstore documents

    Args:
        pdf_elements (List[Element]): All parsed elements from the PDF.

    Returns:
        Tuple[List[Document], List[Document]]:
            - Summary documents for vector store
            - Raw text documents for doc store
    """
    # Step 1: Further chunk PDF elements using titles
    chunked_elements = make_chunks(pdf_elements)

    # Step 2: Extract text content only from the chunked elements
    texts, text_elements, _, _ = elements_wise_extractor(chunked_elements, "CompositeElement")

    # Step 3: Generate summaries (cached if exists)
    summaries = reload_json("summaries/text_summaries.json", summarize_texts, texts)

    # Step 4: Convert into Langchain Documents
    doc_for_vectorstore, doc_for_docstore = text_to_documents(text_elements, texts, summaries)

    return doc_for_vectorstore, doc_for_docstore