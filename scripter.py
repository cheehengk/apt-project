from PyPDF2 import PdfReader
import openai

openai.api_key = "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"

def extract_pdf(path):
    pdfReader = PdfReader(path)
    num_pages = len(pdfReader.pages)
    print("Number of Pages: ", num_pages)

    text_data = []

    for i in range(num_pages):
        text_data.append(pdfReader.pages[i].extract_text())

    return text_data, num_pages


def get_openai_summary(text_data):
    prompt = "Summarise this piece of text to 50% of its original length. " + text_data
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

for i in range(num_pages):
    print("Page ", i + 1)
    page_summary = get_openai_summary(text[i])
    print(page_summary)
