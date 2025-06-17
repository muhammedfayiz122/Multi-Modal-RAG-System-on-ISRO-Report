
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

def summarize_texts(texts: str) -> List[str]:
    summaries, error_rows = summarize_text_sequencial(texts)
    logging.info(f"{len([i for i in summaries if i])} texts summarized out of {len(texts)}")
    if error_rows:
        logging.info(f"summary unssuccessful on {error_rows}")
    return summaries

def summarize_tables(tables: str) -> List[str]:
    summaries = summarize_table_sequencial(tables)
    logging.info(f"{len([i for i in summaries if i])} tables summarized out of {len(tables)}")
    return summaries

def summarize_images(img_path: str, output_dir="") -> List[str]:
    img_base64_list, summaries, error_images = generate_img_summary(img_path)
    logging.info(f"{len([i for i in summaries if i])} images summarized out of {len(os.listdir(img_path))}")
    return summaries, img_base64_list
    
def generate_key(limit):
    return [str(uuid4()) for _ in limit]

def image_to_base64(path):
    image_names = sorted(os.listdir(path))
    return [encode_image(os.path.join(path, img_path)) for img_path in image_names]

def text_to_documents(text_elements, raw_text, summary_text):
    """
    """
    text_ids = reload_json("ids/text_ids.json", generate_key, raw_text)
    doc_for_vectorstore = [] # summary (for fast semantic search)
    doc_for_docstore = []    # full/raw content

    for i in range(len(raw_text)):
        # Document for VectorStore
        vs_doc = Document(
            page_content=summary_text[i],
            metadata={  
                "type": "Text",
                "page_number": text_elements[i].metadata.page_number,
                "doc_id": text_ids[i]
            }
        )
        doc_for_vectorstore.append(vs_doc)

        # Document for DocStore
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

def table_to_documents(table_elements, raw_table, table_summaries):
    """
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

def image_to_documents(fpath, img_elements, img_summaries, bs64_images):
    """
    """
    doc_for_vectorstore = [] # summary (for fast semantic search)
    doc_for_docstore = []    # full/raw content
    image_names = sorted(os.listdir(fpath))
    image_ids = reload_json("ids/image_ids.json", generate_key, image_names)
    img_elements = sorted([element for element in img_elements if element.metadata.image_path.split(sep="\\")[-1] in image_names], key=lambda element: element.metadata.image_path)
    
    if len(image_names) != len(img_summaries):
        logging.info(f"Length mismatch: {len(image_names)} image files, {len(img_summaries)} image summaries, Ignore : {len(img_elements)} image elements")
        raise ValueError(f"Length mismatch: {len(image_names)} image files, {len(img_summaries)} image summaries, Ignore : {len(img_elements)} image elements")
    
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
        doc_for_vectorstore.append(vs_doc)

        # Document for DocStore
        ds_doc = Document(
            page_content=bs64_images[i],
            metadata={
                "type": "Image",
                "page_number": page_no,
                "doc_id": image_ids[i]
            }
        )
        doc_for_docstore.append(ds_doc)

    return doc_for_vectorstore, doc_for_docstore


def pdf_extractor(file_path):
    # Extracting all elements from pdf
    images_path = os.path.join(os.path.dirname(file_path), "extracted_images")
    os.makedirs(images_path, exist_ok=True)

    pdf_elements = reload_pickle("pdf_elements.pkl", extractor, file_path, images_path)
    logging.info(f"Extracting elements from pdf completed : {len(pdf_elements)}")

    # Separating Categories
    images, img_elements, tables, table_elements = reload_pickle("categorized_elements.pkl", elements_wise_extractor, pdf_elements, "Image", "Table")
    logging.info(f"Categorizing completed : Images={len(images)} , image_Elements={len(img_elements)} , Tables={len(tables)} , {len(table_elements)}")

    # Making table summaries
    table_summaries = reload_json("summaries/table_summaries.json", summarize_tables, tables)
    table_vs_doc, table_ds_doc = table_to_documents(table_elements, tables, table_summaries)

    # Making image summaries
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
    pdf_extractor(file_name)
    logging.info("############### <test ok> #####################")

# def extract_text_from_pdf(pdf_path: str) -> List[str]: ...
# def extract_tables_from_pdf(pdf_path: str) -> List[pd.DataFrame]: ...
# def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[str]: ...
# def extract_captions(pdf_path: str) -> Dict[str, str]: ...
