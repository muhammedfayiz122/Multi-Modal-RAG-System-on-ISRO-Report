from pdf_loader import pdf_extractor
from chunker import text_chunker
from vectorstore import get_retriever, add_documents
from utils.logger import logging

def main():
    pdf_path = r"../data/ISRO_annual_report_24-25.pdf"
    result = pdf_extractor(pdf_path)
    pdf_elements = result["elements"]

    table_summary_doc, table_raw_doc = result["table_summary"], result["table_raw"]
    img_summary_doc, img_raw_doc = result["img_summary"], result["img_raw"]
    text_summary_doc, text_raw_doc = text_chunker(pdf_elements)

    retriever = get_retriever()

    add_documents(retriever, text_summary_doc, text_raw_doc)
    add_documents(retriever, table_summary_doc, table_raw_doc)
    add_documents(retriever, img_summary_doc, img_raw_doc)


if __name__ == "__main__":
    main()
