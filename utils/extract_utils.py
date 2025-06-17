
# from unstructured.partition.pdf import partition_pdf
import partition_pdf
from utils.logger import logging

def extractor(file_name, images_path="extracted_images"):
    """
    Extract the pdf
    """
    pdf_elements = partition_pdf(
        filename=file_name,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=False,
        extract_image_block_output_dir=images_path
    )
    return pdf_elements

def elements_wise_extractor(pdf_elements, category1, category2=None):
    if not category1:
        logging.info("Error : {category} not given")
    raw_1, elements_1 = [], []
    raw_2, elements_2 = [], []
    for element in pdf_elements:
        cls_name = element.__class__.__name__
        if cls_name == category1:
            elements_1.append(element)
            raw_1.append(str(element))
        elif cls_name == category2:
            elements_2.append(element)
            raw_2.append(str(element))
    if not raw_1:
        logging.info(f"{category1} not found")

    return raw_1, elements_1, raw_2, elements_2