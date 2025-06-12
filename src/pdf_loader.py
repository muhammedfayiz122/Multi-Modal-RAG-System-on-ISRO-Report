
from typing import List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.save_load_files import reload
from utils.extract_utils import extractor, elements_wise_extractor
from utils.image_processing import generate_img_summary
from utils.table_processing import summarize_table_batch

def extract_text_from_pdf(pdf_path: str) -> List[str]:
    pass

def extract_tables_from_pdf(pdf_path: str) -> List[str]:
    pass

def extract_images_from_pdf(img_path: str, output_dir: str) -> List[str]:
    summaries = reload("img_summaries.pkl", generate_img_summary, img_path)
    
    

def pdf_extractor(file_path):
    pdf_elements = reload("pdf_elements.pkl", extractor, file_path)
    extracted_elements = reload("categorized_elements", elements_wise_extractor, pdf_elements)
    for key in extracted_elements:
        print(key, " ", len(extracted_elements[key]))

if __name__ == "__main__":
    file_name = r"../data/ISRO_annual_report_24-25.pdf"
    pdf_extractor(file_name)

# def extract_text_from_pdf(pdf_path: str) -> List[str]: ...
# def extract_tables_from_pdf(pdf_path: str) -> List[pd.DataFrame]: ...
# def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[str]: ...
# def extract_captions(pdf_path: str) -> Dict[str, str]: ...
