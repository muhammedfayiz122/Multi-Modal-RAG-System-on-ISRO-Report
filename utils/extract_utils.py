
from unstructured.partition.pdf import partition_pdf

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

def elements_wise_extractor(pdf_elements):
    # Assign each key as a variable dynamically
    extracted_elements = {}
    for element in pdf_elements:
        class_name = element.__class__.__name__
        extracted_elements.setdefault(class_name, []).append(str(element))
    return extracted_elements