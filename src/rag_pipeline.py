# def generate_answer(query: str) -> str: ...
# def retrieve_context(query: str) -> List[str]: ...
# def summarize_chunks(chunks: List[str]) -> str: ...
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain_core.prompts import PromptTemplate 
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

def format_doc(doc):
    # Filter metadata to exclude 'doc_id'
    filtered_meta = {k: v for k, v in doc.metadata.items() if k != "doc_id"}
    meta_str = ", ".join(f"{k}: {v}" for k, v in filtered_meta.items())
    return f"[Metadata: {meta_str}]\n{doc.page_content}"


def split_image_text_types(docs):
    """
    """
    images = []
    texts = []
    tables = [] 

    if not docs:
        return []

    for doc in docs:
        if doc.metadata.get("type") == "Image":
            if not isinstance(doc.page_content, str):
                print(f"Warning: Skipping non-string image content: {type(doc.page_content)}")
                continue
            # its image
            resized_image = resize_base64_images(doc.page_content, size=(1300, 600))
            images.append(resized_image)

        elif doc.metadata.get("type") == "Table":
            # its table
            tables.append(doc)
        else:
            # its text
            texts.append(doc)

    logging.info(f"retrieved status : images={len(images)}, texts={len(texts)}, tables: {len(tables)}")
    return {"images": images, "texts": texts, "tables": tables}


def img_prompt_func(data):
    """
    Prepares messages for GPT-4 Vision with images, texts, and tables.
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
    For creating RAG chain
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
    pdf_path = os.path.join(get_project_root(), "data", "ISRO_annual_report_24-25.pdf")
    result = pdf_extractor(pdf_path)
    pdf_elements = result["elements"]

    table_summary_doc, table_raw_doc = result["table_summary"], result["table_raw"]
    img_summary_doc, img_raw_doc = result["img_summary"], result["img_raw"]
    text_summary_doc, text_raw_doc = text_chunker(pdf_elements)

    retriever = get_retriever()

    add_documents(retriever, text_summary_doc, text_raw_doc)
    add_documents(retriever, table_summary_doc, table_raw_doc)
    add_documents(retriever, img_summary_doc, img_raw_doc)

    # print(retriever.invoke("which are the rockets they launched"))

    rag_chain = create_rag_chain(retriever)

    return rag_chain

def answer_query(query):
    retriever = get_retriever()
    rag_chain = create_rag_chain(retriever)
    return rag_chain.invoke(query)


