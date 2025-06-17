from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import time

load_dotenv()


def text_chain():
    template = """
    You are an assistant tasked with summarizing text .
    Give a concise summary of the text.
    This text are from ISRO annual report.

    Respond only with the summary, no additional comment.
    Do not start your message by saying "Here is a summary" or anything like that.
    Just give the summary as it is.

    \nText : {element}
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



def summarize_text_sequencial(texts):
    """
    """ 
    error_row = []
    text_summaries = []
    summarize_chain = text_chain()
    for i, row in enumerate(texts):
        try:
            summary = summarize_chain.invoke(row)
            text_summaries.append(summary)
            time.sleep(1)
        except Exception as e:
            retry = 0
            while not summary:
                retry += 1
                if retry > 4:
                    break
                time.sleep(4)
                try:
                    summary = summarize_chain.invoke(row)
                    text_summaries.append(summary)
                    time.sleep(1)
                except Exception as e:
                    print(e)
            time.sleep(4)
    return text_summaries, error_row

def summarize_text_batch(text):
    summarize_chain = text_chain()
    try:
        table_summaries = summarize_chain.batch(text, {"max_concurrency": 3})
    except Exception as e:
        print(f"Error in summarizing table : {e}")
        print(f"Total summarized = {len(table_summaries)}")
    return table_summaries
