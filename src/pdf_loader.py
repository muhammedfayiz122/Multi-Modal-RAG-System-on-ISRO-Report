
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.save_load_files import reload

def process_text(texts):
    pass

def process_images(images):
    pass

def process_tables(tables):
    pass





def pdf_extractor(file_path):
    pdf_elements = reload("pdf_elements.pkl", extractor, file_path)
    extracted_elements = reload("categorized_elements", elements_wise_extractor, pdf_elements)
    print(extracted_elements.keys())

if __name__ == "__main__":
    file_name = r"../data/ISRO_annual_report_24-25.pdf"
    pdf_extractor(file_name)