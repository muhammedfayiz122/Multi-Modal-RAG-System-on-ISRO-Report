import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage
from utils.image_processing import resize_base64_images
from utils.paths import get_project_root
from pdf_loader import pdf_extractor
from chunker import text_chunker
from vectorstore import get_retriever, add_documents
from utils.logger import logging
from langchain_core.documents import Document

"""
rag_pipeline.py

This module defines the RAG pipeline using Langchain and Gemini models.
It handles:
- PDF loading and chunking
- Document indexing to Milvus + MongoDB
- Query formatting for text/table/image inputs
- Response generation using Gemini multimodal model
"""

def format_doc(doc: Document) -> str:
    """
    Format a Langchain document with its metadata for display.

    Args:
        doc (Document): A Langchain document.

    Returns:
        str: Formatted string including metadata and content.
    """
    filtered_meta = {k: v for k, v in doc.metadata.items() if k != "doc_id"}
    meta_str = ", ".join(f"{k}: {v}" for k, v in filtered_meta.items())
    return f"[Metadata: {meta_str}]\n{doc.page_content}"


def split_image_text_types(docs: Document) -> dict:
    """
    Splits retrieved documents into images, tables, and texts.

    Args:
        docs (List[Document]): Retrieved documents from retriever.

    Returns:
        dict: Separated lists of images (base64), texts, and tables.
    """
    images, texts, tables = [], [], [] 
    if not docs:
        return {"images": [], "texts": [], "tables": []}

    for doc in docs:
        dtype = doc.metadata.get("type")
        if dtype == "Image":
            if not isinstance(doc.page_content, str):
                print(f"Warning: Skipping non-string image content: {type(doc.page_content)}")
                continue
            resized_image = resize_base64_images(doc.page_content, size=(1300, 600))
            images.append(resized_image)
        elif dtype == "Table":
            tables.append(doc)
        else:
            texts.append(doc)

    logging.info(f"retrieved status : images={len(images)}, texts={len(texts)}, tables: {len(tables)}")
    return {"images": images, "texts": texts, "tables": tables}


def img_prompt_func(data):
    """
    Builds a prompt (with multimodal context) for the LLM using text, table, and image inputs.

    Args:
        data (dict): Should include a 'context' dict and a 'question' string.

    Returns:
        List[HumanMessage]: Message format accepted by Gemini/GPT-4V.
    """
    images = data["context"].get("images", [])
    texts = data["context"].get("texts", [])
    tables = data["context"].get("tables", [])
    question = data.get("question", "")

    messages = []

    # Add images
    for img in images:
        messages.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img}"},
        })

    # Prepare table section (merge into main text message)
    combined_text = "\n".join(format_doc(doc) for doc in texts)
    if tables:
        table_block = "\n\n[Table Data]\n" + "\n\n".join(format_doc(doc) for doc in tables)
        combined_text += table_block

    # Final text message
    prompt_text = (f"""
        You are an assistant tasked with answering user query.
        Use the following piece of retrived context (text and/or images and/or tables) to answer user queries.
        if Context is non related to user question ignore it."
                   
        User Question:{question}

        Context:
        {combined_text}
        """
    )

    messages.append({
        "type": "text",
        "text": prompt_text,
    })
    logging.info(f"query sent to LLM : {combined_text}")
    return [HumanMessage(content=messages)]


def create_rag_chain(retriever):
    """
    Creates the complete RAG pipeline with retrieval and LLM response generation.

    Args:
        retriever (MultiVectorRetriever): Retriever for fetching docs.

    Returns:
        Runnable: Executable Langchain pipeline.
    """
    # Model
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    #chain
    rag_chain =  (
        {"context": retriever | RunnableLambda(split_image_text_types), "question": RunnablePassthrough() } 
        | RunnableLambda(img_prompt_func)
        | model 
        |StrOutputParser()
    )
    return rag_chain

def get_rag_pipeline():
    """
    Builds the RAG pipeline after extracting and indexing all data.

    Returns:
        Runnable: RAG chain ready to run.
    """
    pdf_path = os.path.join(get_project_root(), "data", "ISRO_annual_report_24-25.pdf")
    result = pdf_extractor(pdf_path)

    # Extracted documents
    pdf_elements = result["elements"]
    table_summary_doc, table_raw_doc = result["table_summary"], result["table_raw"]
    img_summary_doc, img_raw_doc = result["img_summary"], result["img_raw"]

    # Text chunking
    text_summary_doc, text_raw_doc = text_chunker(pdf_elements)

    # Initialize and fill retriever
    retriever = get_retriever()
    add_documents(retriever, text_summary_doc, text_raw_doc)
    add_documents(retriever, table_summary_doc, table_raw_doc)
    add_documents(retriever, img_summary_doc, img_raw_doc)

    rag_chain = create_rag_chain(retriever)
    return rag_chain

def answer_query(query: str) -> str:
    """
    Handles answering a query via RAG pipeline.

    Args:
        query (str): User's natural language question.

    Returns:
        str: Final answer generated by the LLM.
    """
    retriever = get_retriever()
    rag_chain = create_rag_chain(retriever)
    return rag_chain.invoke(query)


