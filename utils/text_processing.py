from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time

def text_chain():

    template = """
    You are an assistant tasked with summarizing text .
    Give a concise summary of the text.
    This text are from ISRO annual report.

    Respond only with the summary, no additional comment.
    Do not start your message by saying "Here is a summary" or anything like that.
    Just give the summary as it is.

    Text : {element}

    """
    prompt = ChatPromptTemplate.from_template(template)

    model = ChatGroq(temperature=0.5, model="llama-3.1-8b-instant")

    chain = (
        {"element" : lambda x: x}
        | prompt
        | model
        | StrOutputParser()
    )

    return chain



def summarize_text_sequencial(table):
    """
    """ 
    error_text = []
    text_summaries = []
    summarize_chain = text_chain()
    for i, row in enumerate(table):
        try:
            summary = summarize_chain.invoke(row)
            text_summaries.append(summary)
            time.sleep(1)
        except Exception as e:
            print(f"error on {i}th text : {e}")
            error_text.append(i)
            text_summaries.append(None)
            time.sleep(4)

def summarize_text_batch(text):
    summarize_chain = text_chain()
    try:
        table_summaries = summarize_chain.batch(text, {"max_concurrency": 3})
    except Exception as e:
        print(f"Error in summarizing table : {e}")
        print(f"Total summarized = {len(table_summaries)}")
    return table_summaries
