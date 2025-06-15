
from typing import List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.save_load_files import reload_pickle, reload_json
from utils.extract_utils import extractor, elements_wise_extractor
from utils.image_processing import generate_img_summary
from utils.table_processing import summarize_table_sequencial
# from utils.text_processing import summarize_text_sequencial
from utils.logger import logging

# def extract_text_from_pdf(texts: str) -> List[str]:
#     summaries = summarize_text_batch(texts)
#     logging.info(f"{len([i for i in summaries if i])} texts summarized out of {len(texts)}")
#     return summaries

def extract_tables_from_pdf(tables: str) -> List[str]:
    summaries = summarize_table_sequencial(tables)
    logging.info(f"{len([i for i in summaries if i])} tables summarized out of {len(tables)}")
    return summaries

def extract_images_from_pdf(img_path: str, output_dir="") -> List[str]:
    summaries = generate_img_summary(img_path)
    logging.info(f"{len([i for i in summaries if i])} images summarized out of {len(os.listdir(img_path))}")
    return summaries
    
    

def pdf_extractor(file_path):
    # Extracting all elements from pdf
    images_path = os.path.join(os.path.dirname(file_path), "extracted_images")
    os.makedirs(images_path, exist_ok=True)
    pdf_elements = reload_pickle("pdf_elements.pkl", extractor, file_path, images_path)
    logging.info(f"Extracting elements from pdf completed : {len(pdf_elements)}")

    # Separating Categories
    extracted_elements = reload_pickle("categorized_elements.pkl", elements_wise_extractor, pdf_elements)
    logging.info(f"Categorizing completed : {extracted_elements.keys()}")

    # Making table summaries
    tables = extracted_elements["Table"]
    table_summaries = reload_json("table_summaries.json", extract_tables_from_pdf, tables)

    # Making image summaries
    # images = extracted_elements["Images"]
    image_summaries = reload_json("image_summaries.json", extract_images_from_pdf, images_path)

    return pdf_elements, table_summaries, image_summaries


if __name__ == "__main__":
    file_name = r"../data/ISRO_annual_report_24-25.pdf"
    pdf_extractor(file_name)
    logging.info("############### <test ok> #####################")

# def extract_text_from_pdf(pdf_path: str) -> List[str]: ...
# def extract_tables_from_pdf(pdf_path: str) -> List[pd.DataFrame]: ...
# def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[str]: ...
# def extract_captions(pdf_path: str) -> Dict[str, str]: ...
