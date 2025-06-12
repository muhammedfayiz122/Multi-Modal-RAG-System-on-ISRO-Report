# def generate_answer(query: str) -> str: ...
# def retrieve_context(query: str) -> List[str]: ...
# def summarize_chunks(chunks: List[str]) -> str: ...

from langchain_core.prompts import PromptTemplate 
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough

def create_rag_chain(retriever):
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
    retrieval_chain = (
        {"context" : retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | parser
    )
    return retrieval_chain
