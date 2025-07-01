
from langchain_core.documents import Document
from uuid import uuid4
from typing import List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.save_load_files import reload_pickle, reload_json
from utils.extract_utils import extractor, elements_wise_extractor
from utils.image_processing import generate_img_summary, encode_image
from utils.table_processing import summarize_table_sequencial
from utils.text_processing import summarize_text_sequencial
from utils.logger import logging

"""
pdf_loader.py

Responsible for:
- Extracting elements from ISRO PDF (text, tables, images)
- Generating summaries for different content types
- Converting extracted elements to Langchain Documents
"""

def summarize_texts(texts: str) -> List[str]:
    """
    Generates summaries for a list of raw text blocks.

    Args:
        texts (List[str]): Extracted raw text chunks.

    Returns:
        List[str]: Corresponding summaries for each chunk.
    """
    summaries, error_rows = summarize_text_sequencial(texts)
    logging.info(f"{len([i for i in summaries if i])} texts summarized out of {len(texts)}")
    if error_rows:
        logging.info(f"summary unssuccessful on {error_rows}")
    return summaries

def summarize_tables(tables: List[str]) -> List[str]:
    """
    Summarizes tabular data extracted from PDF.

    Args:
        tables (List[str]): Extracted tables.

    Returns:
        List[str]: Summaries for each table.
    """
    summaries = summarize_table_sequencial(tables)
    logging.info(f"{len([i for i in summaries if i])} tables summarized out of {len(tables)}")
    return summaries

def summarize_images(img_path: str, output_dir: str="") -> List[str]:
    """
    Generates summaries for all images in a directory.

    Args:
        img_path (str): Folder containing extracted images.
        output_dir (str, optional): Directory for storing output summaries. Defaults to "".

    Returns:
        List[str]: Summary strings and encoded base64 versions.
    """
    img_base64_list, summaries, error_images = generate_img_summary(img_path)
    logging.info(f"{len([i for i in summaries if i])} images summarized out of {len(os.listdir(img_path))}")
    return summaries, img_base64_list
    
def generate_key(limit: List) -> List[str]:
    """
    Generates a list of UUIDs matching the length of given input.

    Args:
        limit (List): Any list (just for length).

    Returns:
        List[str]: Unique UUIDs as string.
    """
    return [str(uuid4()) for _ in limit]

def image_to_base64(path: str) -> List[str]:
    """
    Converts all image files in a directory to base64 strings.

    Args:
        path (str): Path to folder with images.

    Returns:
        List[str]: Base64-encoded image strings.
    """
    image_names = sorted(os.listdir(path))
    return [encode_image(os.path.join(path, img_path)) for img_path in image_names]

def text_to_documents(text_elements: List, raw_text: List, summary_text: List):
    """
    Converts raw/summarized texts into Langchain Document format.

    Args:
        text_elements (List[Element]): Unstructured elements with metadata.
        raw_text (List[str]): Original extracted texts.
        summary_text (List[str]): Summarized versions.

    Returns:
        Tuple[List[Document], List[Document]]:
            - For Vector Store (summary)
            - For Doc Store (raw)
    """
    text_ids = reload_json("ids/text_ids.json", generate_key, raw_text)
    doc_for_vectorstore = [] # summary (for fast semantic search)
    doc_for_docstore = []    # full/raw content

    for i in range(len(raw_text)):
        # Summary document for VectorStore
        vs_doc = Document(
            page_content=summary_text[i],
            metadata={  
                "type": "Text",
                "page_number": text_elements[i].metadata.page_number,
                "doc_id": text_ids[i]
            }
        )
        doc_for_vectorstore.append(vs_doc)

        # Raw document for DocStore
        ds_doc = Document(
            page_content=raw_text[i],
            metadata={  
                "type": "Text",
                "page_number": text_elements[i].metadata.page_number,
                "doc_id": text_ids[i]
            }
        )
        doc_for_docstore.append(ds_doc)

    return doc_for_vectorstore, doc_for_docstore

def table_to_documents(table_elements: List, raw_table: List, table_summaries: List):
    """
    Converts table elements to Langchain documents.

    Args:
        table_elements (List[Element]): Table elements from PDF.
        raw_table (List[str]): Original tables.
        table_summaries (List[str]): Summarized table text.

    Returns:
        Tuple[List[Document], List[Document]]: Summary + raw versions
    """
    table_ids = reload_json("ids/table_ids.json", generate_key, table_summaries)
    doc_for_vectorstore = [] # summary (for fast semantic search)
    doc_for_docstore = []    # full/raw content

    for i,element in enumerate(table_elements):
        # Document for VectorStorev
        vs_doc = Document(
            page_content=table_summaries[i],
            metadata={
                "type": "Table",
                "page_number": element.metadata.page_number,
                "doc_id": table_ids[i]
            }
        )
        doc_for_vectorstore.append(vs_doc)

        # Document for DocStore
        ds_doc = Document(
            page_content=table_summaries[i],
            metadata={
                "type": "Table",
                "page_number": element.metadata.page_number,
                "doc_id": table_ids[i]
            }
        )
        doc_for_docstore.append(ds_doc)
    return doc_for_vectorstore, doc_for_docstore

def image_to_documents(fpath: str, img_elements: List, img_summaries: List, bs64_images: List):
    """
    Converts image summaries + base64 to Langchain documents.

    Args:
        fpath (str): Directory of image files.
        img_elements (List[Element]): Extracted image elements.
        img_summaries (List[str]): Image captions/summaries.
        bs64_images (List[str]): Base64 versions.

    Returns:
        Tuple[List[Document], List[Document]]: Summary + raw versions
    """
    doc_for_vectorstore = [] # summary (for fast semantic search)
    doc_for_docstore = []    # full/raw content
    image_names = sorted(os.listdir(fpath))
    image_ids = reload_json("ids/image_ids.json", generate_key, image_names)

    img_elements = sorted(
        [element for element in img_elements if element.metadata.image_path.split(sep="\\")[-1] in image_names],
        key=lambda element: element.metadata.image_path
    )
    
    # Validation
    if len(image_names) != len(img_summaries):
        logging.info(f"Length mismatch: {len(image_names)} files, {len(img_summaries)} summaries.")
        raise ValueError("Mismatch between images and summaries.")
    
    if image_names != [element.metadata.image_path.split(sep="\\")[-1] for element in img_elements] :
        logging.info(f"Image elements are not equal to images in {fpath}")
        raise ValueError(f"Image elements are not equal to images in {fpath}")

    for i, element in enumerate(img_elements):
        page_no = element.metadata.page_number

        # Document for VectorStore
        vs_doc = Document(
            page_content=img_summaries[i],
            metadata={
                "type": "Image",
                "page_number": page_no,
                "doc_id": image_ids[i]
            }
        )

        # Raw image as base64 for docstore
        ds_doc = Document(
            page_content=bs64_images[i],
            metadata={
                "type": "Image",
                "page_number": page_no,
                "doc_id": image_ids[i]
            }
        )

        doc_for_vectorstore.append(vs_doc)
        doc_for_docstore.append(ds_doc)

    return doc_for_vectorstore, doc_for_docstore


def pdf_extractor(file_path):
    """
    Main PDF processing pipeline:
    - Extracts raw elements (text, images, tables) from PDF
    - Categorizes elements
    - Generates summaries and encodings
    - Converts to Langchain-compatible Documents

    Args:
        file_path (str): Path to the input PDF file.

    Returns:
        dict: A dictionary with all processed document types:
            {
                "elements": [...],
                "table_summary": [...],
                "table_raw": [...],
                "img_summary": [...],
                "img_raw": [...],
            }

    Raises:
        ValueError: If there's a mismatch between extracted and summarized content.
    """
    # Folder to store extracted images
    images_path = os.path.join(os.path.dirname(file_path), "extracted_images")
    os.makedirs(images_path, exist_ok=True)

    # Extract all elements (text, tables, images, etc.)
    pdf_elements = reload_pickle("pdf_elements.pkl", extractor, file_path, images_path)
    logging.info(f"Extracting elements from pdf completed : {len(pdf_elements)}")

    # Separate images and tables
    images, img_elements, tables, table_elements = reload_pickle(
        "categorized_elements.pkl", elements_wise_extractor, pdf_elements, "Image", "Table"
    )
    logging.info(f"Categorized : Images={len(images)} , image_Elements={len(img_elements)} , Tables={len(tables)} , {len(table_elements)}")

   # Summarize table data
    table_summaries = reload_json("summaries/table_summaries.json", summarize_tables, tables)
    table_vs_doc, table_ds_doc = table_to_documents(table_elements, tables, table_summaries)

    # Summarize image data
    img_summaries = reload_json("summaries/image_summaries.json", summarize_images, images_path)
    bs64_images = reload_json("encodes/image_encodes.json", image_to_base64, images_path)
    img_vs_doc, img_ds_doc  = image_to_documents(images_path, img_elements, img_summaries, bs64_images)

    return {
        "elements": pdf_elements,
        "table_summary": table_vs_doc,
        "table_raw": table_ds_doc,
        "img_summary": img_vs_doc,
        "img_raw": img_ds_doc
    }


if __name__ == "__main__":
    file_name = r"../data/ISRO_annual_report_24-25.pdf"
    try:
        results = pdf_extractor(file_name)
        logging.info("✅ PDF extraction and processing completed successfully.")
    except Exception as e:
        logging.error(f"❌ Error in PDF processing: {e}")
