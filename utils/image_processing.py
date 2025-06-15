from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from PIL import Image
import base64
import time
import io
import os

load_dotenv()

def encode_image(image_path: str) -> str:
    """Getting the base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def img_summarizer(img_base64: str) -> str:
    """
    Calling LLM to generate summary
    """
    prompt = """ You are an assistant tasked with summarize image for semantic search. \
    These summaries will be ambedded and used to retrieve raw image. \
    This image is taken from ISRO annual report. \
    Give a consise summary of the image that is well optimized for retrieval.

    """
    # Custom message template
    message = [
        SystemMessage(
            content="You are a helpful assistant."
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpg;base64,{img_base64}"}
                }
            ]
        )
    ]

    # Model
    model =  ChatGoogleGenerativeAI(model="gemini-1.5-flash", max_tokens=1024)

    # Calling LLM to summarize
    summary = model.invoke(message)

    return summary

def generate_img_summary(path: str):
    """
    Generate summaries and base64 encoded strings for images
    path: Path to list of .jpg files extracted by Unstructured
    """

    # Store base64 encoded images
    img_base64_list = []

    # Store image summaries
    img_summaries = []

    # Tracking error when generating summary
    error_images = []

    # Apply to images
    for img_file in sorted(os.listdir(path)):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(path, img_file)
            try:
                base64_image = encode_image(img_path)
                img_base64_list.append(base64_image)
                summary  = img_summarizer(base64_image)
                if summary:
                    img_summaries.append(summary)
                else:
                    img_summaries.append(None)
                    error_images.append(img_path)
                time.sleep(5)
            except Exception as e:
                print(f"error in {img_path} : {e}")
                img_summaries.append(None)
                error_images.append(img_path)
                time.sleep(8)
    return img_base64_list, img_summaries, error_images

def resize_base64_images(base64_string, size=(128, 128)):
    """
    function for resize images that we can easily feed into models
    """
    # Decode the Base64 string
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))

    # Resize the image
    resized_img = img.resize(size, Image.LANCZOS)

    # Save the resized image to a bytes buffer
    buffered = io.BytesIO()
    resized_img.save(buffered, format=img.format)

    # Encode the resized image to Base64
    return base64.b64ecode(buffered.getvalue()).decode("utf-8")
