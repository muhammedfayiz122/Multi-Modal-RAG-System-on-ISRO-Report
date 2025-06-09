from unstructured.partition.pdf import partition_pdf
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.save_load_files import reload

def extractor(file_name):
    """
    Extract the pdf
    """
    pdf_elements = partition_pdf(
        filename=file_name,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=False,
        extract_image_block_output_dir="temp_ISRO"
    )
    return pdf_elements


def elements_extractor(pdf_elements):
    # Assign each key as a variable dynamically
    extracted_elements = {}
    for element in pdf_elements:
        class_name = element.__class__.__name__
        extracted_elements.setdefault(class_name, []).append(str(element))
    # Image
    # NarrativeText
    # Title
    # Text
    # ListItem
    # Table
    # FigureCaption
    # Header
    return extracted_elements

def pdf_extractor(file_path):
    pdf_elements = reload("pdf_elements.pkl", extractor, file_path)
    extracted_elements = reload("categorized_elements", elements_extractor, pdf_elements)
    print(extracted_elements.keys())
    


if __name__ == "__main__":
    file_name = r"../data/ISRO_annual_report_24-25.pdf"
    pdf_extractor(file_name)