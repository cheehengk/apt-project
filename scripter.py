import time
import openai
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests

openai.api_key = "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"
pixabay_api_key = "36447779-8e6272c9ff054351cb18d32ff"


def extract_pdf(path):
    with open(path) as f:
        pdf_docu = f.read()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 100,
        chunk_overlap  = 20,
        length_function = len,
    )

    texts = text_splitter.create_documents([pdf_docu])
    for i in range(texts):
        print(texts[i])

    return texts


def generate_video_script(text_data):
    prompt = "Give me a short video transcript and keyword at the start describing: " + text_data

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


def get_images(keyword_array):
    for index, key in enumerate(keyword_array):
        url = "https://pixabay.com/api/?key=36447779-8e6272c9ff054351cb18d32ff&q=" + key + "&image_type=photo"
        image_result = requests.get(url).json()
        image_url = image_result['hits'][0]['largeImageURL']

        image_response = requests.get(image_url)

        if image_response.status_code:
            filepath = "Images/" + str(index) + ".jpg"
            fp = open(filepath, 'wb')
            fp.write(image_response.content)
            fp.close()


def get_audios(script_array):
    for index, scr in enumerate(script_array):
        url = "https://play.ht/api/v1/convert"

        content = scr
        payload = {
            "content": [content],
            "voice": "en-US-JennyNeural"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "AUTHORIZATION": "2678135098fb4da7b280ab7a0ff79073",
            "X-USER-ID": "067LoF4jArN6VRzoheup5ImrEId2"
        }

        audio_response = requests.post(url, json=payload, headers=headers).json()

        transcription_code = audio_response['transcriptionId']

        url = "https://play.ht/api/v1/articleStatus?transcriptionId=" + transcription_code

        headers = {
            "accept": "application/json",
            "AUTHORIZATION": "2678135098fb4da7b280ab7a0ff79073",
            "X-USER-ID": "067LoF4jArN6VRzoheup5ImrEId2"
        }

        audio_url_response = requests.get(url, headers=headers).json()
        print(audio_url_response)

        while not audio_url_response['converted']:
            time.sleep(10)
            audio_url_response = requests.get(url, headers=headers).json()
            print(audio_url_response)

        audio_url = audio_url_response['audioUrl']

        audio_get = requests.get(audio_url)

        if audio_get.status_code:
            filepath = "Audios/" + str(index) + ".mp3"
            fp = open(filepath, 'wb')
            fp.write(audio_get.content)
            fp.close()


# Main Program Here
file_path = "testdoc.pdf"
text, num_pages = extract_pdf(file_path)
script = []
keyword = []

for i in range(num_pages):
    result = generate_video_script(text[i])
    script.append(result)
    keyword.append((result.split())[1])
    # time.sleep(10)  # 10 seconds API cooldown

get_images(keyword)
get_audios(script)
