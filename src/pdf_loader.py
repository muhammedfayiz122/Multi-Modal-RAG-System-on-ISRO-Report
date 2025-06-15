
from typing import List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.save_load_files import reload
from utils.extract_utils import extractor, elements_wise_extractor
from utils.image_processing import generate_img_summary
from utils.table_processing import summarize_table_batch
from utils.text_processing import summarize_text_batch
from chunker import 

def extract_text_from_pdf(texts: str) -> List[str]:
    summaries = reload("text_summaries.pkl", summarize_text_batch, texts)
    return summaries

def extract_tables_from_pdf(tables: str) -> List[str]:
    summaries = reload("table_summaries.pkl", summarize_table_batch, tables)
    return summaries

def extract_images_from_pdf(img_path: str, output_dir: str) -> List[str]:
    summaries = reload("img_summaries.pkl", generate_img_summary, img_path)
    return summaries
    
    

def pdf_extractor(file_path):
    # Extracting all elements from pdf
    images_path = os.path.join(os.path.dirname(file_path), "Extracted_Images")
    os.makedirs(images_path, exist_ok=True)
    pdf_elements = reload("pdf_elements.pkl", extractor, file_path, images_path)

    # Separating Categories
    extracted_elements = reload("categorized_elements", elements_wise_extractor, pdf_elements)

    # Making table summaries
    tables = extracted_elements["Tables"]
    table_summaries = extract_tables_from_pdf(tables)

    # Making image summaries
    # images = extracted_elements["Images"]
    image_summaries = extract_images_from_pdf(images_path)

    return pdf_elements, table_summaries, image_summaries


if __name__ == "__main__":
    file_name = r"../data/ISRO_annual_report_24-25.pdf"
    pdf_extractor(file_name)

# def extract_text_from_pdf(pdf_path: str) -> List[str]: ...
# def extract_tables_from_pdf(pdf_path: str) -> List[pd.DataFrame]: ...
# def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[str]: ...
# def extract_captions(pdf_path: str) -> Dict[str, str]: ...
