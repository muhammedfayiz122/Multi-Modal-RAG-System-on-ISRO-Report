from pdf_loader import pdf_extractor
from chunker import text_chunker
from utils.logger import logging

def main():
    pdf_path = r"../data/ISRO_annual_report_24-25.pdf"
    pdf_elements, table_doc, image_doc = pdf_extractor(pdf_path)
    text_docs = text_chunker(pdf_elements, summarize=True)
    print(text_docs[:5])

if __name__ == "__main__":
    main()
