from unstructured.partition.pdf import partition_pdf
import pickle


def extract_pdf(file_name):
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

def save_extracted_files(pdf_elements):
    with open('ISRO_elements.pkl', 'wb') as file: 
        pickle.dump(pdf_elements, file)

def load_extracted_files():
    with open("ISRO_elements.pkl", "rb") as f:
        pdf_elements = pickle.load(f)
    return pdf_elements

def extract_elements(pdf_elements):
    print(f"Total : {len(pdf_elements)}")
    elements_category = set()
    for elements in pdf_elements:
        class_name = elements.__class__.__name__
        elements_category.add(class_name)
    print(f"Categories are : {elements_category}")
    Image = []
    Text = []
    FigureCaption = []
    NarrativeText = []
    Title = []
    ListItem = []
    Header = []
    Table = []
    for elements in pdf_elements:
        class_name = elements.__class__.__name__
        if class_name == "Image":
            Image.append(str(elements))
        elif class_name == "Text":
            Text.append(str(elements))
        elif class_name == "FigureCaption":
            FigureCaption.append(str(elements))
        elif class_name == "NarrativeText":
            NarrativeText.append(str(elements))
        elif class_name == "Title":
            Title.append(str(elements))
        elif class_name == "ListItem":
            ListItem.append(str(elements))
        elif class_name == "Header":
            Header.append(str(elements))
        elif class_name == "Table":
            Table.append(str(elements))
    return Image, Text, FigureCaption, NarrativeText, Title, ListItem, Header, Table

if __name__ == "__main__":
    file_name = r"../src/ISRO_annual_report_24-25.pdf"