import time
import openai
from PyPDF2 import PdfReader

openai.api_key = "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"


def extract_pdf(path):
    pdfReader = PdfReader(path)
    pages = len(pdfReader.pages)
    print("Number of Pages: ", pages)

    text_data = []

    for i in range(pages):
        text_data.append(pdfReader.pages[i].extract_text())

    return text_data, pages


def generate_video_script(text_data):
    prompt = "Give me a short video transcript: " + text_data

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": prompt}
        ],
        temperature=0
    )
    output = response.choices[0].message.content
    return output


# Main Program Here
file_path = "testdoc.pdf"
text, num_pages = extract_pdf(file_path)
script = []

for i in range(num_pages):
    print("Page ", i + 1)
    script.append(generate_video_script(text[i]))
    print(script[i])
    # time.sleep(3)  # 3 seconds delay to cool down API calls
