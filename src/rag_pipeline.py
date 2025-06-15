# def generate_answer(query: str) -> str: ...
# def retrieve_context(query: str) -> List[str]: ...
# def summarize_chunks(chunks: List[str]) -> str: ...

from langchain_core.prompts import PromptTemplate 
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage
from utils.image_processing import resize_base64_images

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
            # its image
            resized_image = resize_base64_images(doc, size=(1300, 600))
            images.append(resized_image)

        elif doc.metadata.get("type") == "Table":
            # its table
            tables.append(doc)
        else:
            # its text
            texts.append(doc)


def img_prompt_func(data):
    """
    Prepares messages for GPT-4 Vision with images, texts, and tables.
    """
    print(data)
    
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
    combined_text = "\n".join(texts)
    if tables:
        table_block = "\n\n[Table Data]\n" + "\n\n".join(tables)
        combined_text += table_block

    # Final text message
    prompt_text = (
        "You are a helpful assistant.\n"
        "Use the following information (text and/or images and/or tables) to answer the user's question.\n\n"
        f"User Question:\n{question}\n\n"
        "Context:\n"
        f"{combined_text}"
    )

    messages.append({
        "type": "text",
        "text": prompt_text,
    })

    return [HumanMessage(content=messages)]


def create_rag_chain(retriever):
    """
    For creating RAG chain
    """
    # Prompt
    template = """You are an assistant tasked with answerign user query.
    Use the following piece of retrived context to anser user queries.
    if Context is non related to query ignore it.
    If you dont know the answer , just say that you don't know.
    keep the answer consise.
    \nQuestion: {question}
    \nContext: {context}
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=['context', 'question'],
    )

    # Model
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    # Output Parser
    parser = StrOutputParser()

    #chain
    rag_chain =  (
        {"context": retriever | RunnableLambda(split_image_text_types), "question": RunnablePassthrough() } 
        | RunnableLambda(img_prompt_func)
        | model 
        |StrOutputParser()
    )
    return rag_chain
