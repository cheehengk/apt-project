import re
import time
import openai
from PyPDF2 import PdfReader
import requests
from langchain.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain import OpenAI, PromptTemplate
from create_video import merge_image_audio, generate_paths, concat_videos
from keys import pixabay_api_key, openai_rotational_keys, number_of_api_keys
from file_cleaner import cleanup
from gtts import gTTS
from random import randint
import string


# os.environ['OPENAI_API_KEY'] = openai_api_key

def load_pdf_file(filepath):
    loader = PyPDFLoader(filepath)
    pages = loader.load_and_split()
    return pages


def custom_prompt(docs):
    # print(docs)
    # docs = [Document(page_content=t) for t in docs]

    prompt_template = """Give a short video transcript based on:
    {text}"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain = load_summarize_chain(OpenAI(temperature=0), chain_type="stuff", prompt=PROMPT)
    return chain.run(docs)


def extract_pdf(path):
    pdfReader = PdfReader(path)
    pages = len(pdfReader.pages)
    print("Number of Pages: ", pages)

    text_data = []

    for i in range(pages):
        text_data.append(pdfReader.pages[i].extract_text())

    return text_data, pages


def get_key(key):
    return openai_rotational_keys[key]


def rotate_key(key):
    new_key = 0 if key == (number_of_api_keys - 1) else key + 1
    print("rotated key from ", key, " to ", new_key)
    return new_key


def slice_script(script):
    words = script.split()
    slices = []
    chunk_size = 10

    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        slices.append(chunk)

    return slices


def generate_video_script(text_data, key):
    openai.api_key = get_key(key)
    prompt = "Give me a short summarised video transcript for this text, shorten the number of words by 70%: " \
             + text_data

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": prompt}
        ],
        temperature=0
    )
    output = slice_script(response.choices[0].message.content)
    return output


def strip_punctuations(text):
    # Remove starting punctuations
    while text and text[0] in string.punctuation:
        text = text[1:]

    # Remove ending punctuations
    while text and text[-1] in string.punctuation:
        text = text[:-1]

    return text


def generate_keyword(text_data, key):
    openai.api_key = get_key(key)
    prompt = "Identify a one word noun which describes this piece of text: " + text_data

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": prompt}
        ],
        temperature=0.5
    )
    output = strip_punctuations(response.choices[0].message.content)
    return output


def get_images(keyword_array):
    for index, key in enumerate(keyword_array):
        url = "https://pixabay.com/api/?key=" + pixabay_api_key + "&q=" + key + "&image_type=photo"
        image_result = requests.get(url).json()

        response = image_result.get('hits', [])
        if len(response):
            rand = randint(0, 2)
            try:
                image_url = response[rand]['largeImageURL']
            except IndexError:
                image_url = "https://pixabay.com/get/gcfcafd5ec3dc85b8b24b0da96ec1b54b078ee9e9a07aefee345f7d885bf5228f15b848036c51797d6d9313e24faeb4972c3d796595133ad3541936b991568d5b_1280.jpg"
        else:
            image_url = "https://pixabay.com/get/gcfcafd5ec3dc85b8b24b0da96ec1b54b078ee9e9a07aefee345f7d885bf5228f15b848036c51797d6d9313e24faeb4972c3d796595133ad3541936b991568d5b_1280.jpg"

        image_response = requests.get(image_url)
        if image_response.status_code:
            filepath = "Images/" + str(index) + ".jpg"
            fp = open(filepath, 'wb')
            fp.write(image_response.content)
            fp.close()


def get_audios(script_array):
    for index, scr in enumerate(script_array):
        speech = gTTS(scr)
        filepath = "Audios/" + str(index) + ".mp3"
        speech.save(filepath)


def main():
    current_openai_key = 0
    text, num_pages = extract_pdf('testdoc.pdf')
    script = []
    keyword = []

    for i in range(num_pages):
        script += generate_video_script(text[i], current_openai_key)
        current_openai_key = rotate_key(current_openai_key)

    print("Number of Scenes: ", len(script))

    for j in range(len(script)):
        keyword.append(generate_keyword(script[j], current_openai_key).split()[0])
        current_openai_key = rotate_key(current_openai_key)
        print(keyword[j])
        time.sleep(10)

    get_images(keyword)
    get_audios(script)

    # Video generation
    image_paths, audio_paths = generate_paths('./Images', './Audios')
    merge_image_audio(image_paths, audio_paths, './Videos', script)
    concat_videos("./Videos")
    cleanup()
    print("Video is successfully produced.")
    for scr in script:
        print(scr + "\n")


if __name__ == '__main__':
    main()
