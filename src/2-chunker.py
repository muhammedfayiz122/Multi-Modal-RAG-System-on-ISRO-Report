from unstructured.chunking.title import chunk_by_title
from pdf_loader import elements_extractor
import matplotlib.pyplot as plt
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from utils.save_load_files import reload, save_as_pickle

def make_chunks(pdf_elements):
    """
    chunk the texts further by the title
    """
    chunked_elements = chunk_by_title(pdf_elements)
    return chunked_elements 

def chunker(pdf_elements):
    """
    """
    chunked_elements = make_chunks(pdf_elements)
    extracted_chunks = elements_extractor(chunked_elements)
    texts = extracted_chunks["CompositeElements"]
    # save_as_pickle(texts, "chunked_texts.pkl")
    return texts

def analyze_category(category, upper_limit=1500, lower_limit=25):
    """
    """
    len_category, upper_count, lower_count, length = [], 0, 0, 0, len(category)
    for i in category:
        len_category.append(len(i))
        if len(i) > upper_limit:
            upper_count += 1
        elif len(i) < lower_limit:
            lower_count += 1

    # Print some samples
    print(f"First three : {category[:3]} ")
    print(f"Last three : {category[-3:]} ")
    print(f"Middle three : {category[(length//2):((length//2)+3)]}")


    # Print Statistics
    print("Length ",len(category))
    print(f"Whole length : {len_category}")
    print(f"Max : {max(len_category)}")
    print(f"Min : {min(len_category)}")
    print(f"Avg : {sum(len_category)/length}")
    print(f"Higher than {upper_limit} : {upper_count}")
    print(f"Higher than {lower_limit} : {lower_count}")

    # Plot histogram 
    plt.hist(len_category, bins=20, edgecolor='black')
    plt.title('Histogram of Category Lengths')
    plt.xlabel('Length')
    plt.ylabel('Frequency')
    plt.show()
