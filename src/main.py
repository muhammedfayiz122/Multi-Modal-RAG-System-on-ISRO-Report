
from rag_pipeline import get_rag_pipeline
from utils.logger import logging

def get_rag():
    

    rag_chain = get_rag_pipeline()
    while 1:
        query = input("Enter your query :")
        try:
            result = rag_chain.invoke(query)
            logging.info(f"result : {result}")
            print(f"Result : \n {result}")
        except Exception as e:
            print(f"Error rag pipeline : {e}")

if __name__ == "__main__":
    get_rag()
