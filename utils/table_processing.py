from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import time

load_dotenv()

def table_chain():
    template = """
    You are an assistant tasked with summarizing tables .
    Give a concise summary of the table.
    This tables are from ISRO annual report.

    Respond only with the summary, no additionnal comment.
    Do not start your message by saying "Here is a summary" or anything like that.
    Just give the summary as it is.

    Table : {element}

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



def summarize_table_sequencial(tables):
    """
    """ 
    error_row = []
    table_summaries = []
    summarize_chain = table_chain()
    for i, row in enumerate(tables):
        try:
            summary = summarize_chain.invoke(row)
            table_summaries.append(summary)
            time.sleep(1)
        except Exception as e:
            print(f"error on table {i} : {e}")
            error_row.append(i)
            table_summaries.append(None)
            time.sleep(4)
    print(f"Total summarized = {len(table_summaries)} out of {len(tables)}")
    return table_summaries

def summarize_table_batch(tables):
    summarize_chain = table_chain()
    table_summaries = []
    try:
        table_summaries = summarize_chain.batch(tables, {"max_concurrency": 3})
    except Exception as e:
        print(f"Error in summarizing table : {e}")
        print(f"Total summarized = {len(table_summaries)} out of {len(tables)}")
    return table_summaries
