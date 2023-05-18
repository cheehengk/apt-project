import time
import openai
from PyPDF2 import PdfReader
import requests
from langchain.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain import OpenAI, PromptTemplate
from create_video import merge_image_audio, generate_paths, concat_videos
from keys import pixabay_api_key, audio_authorisation_key, audio_user_id, openai_rotational_keys, number_of_api_keys
from file_cleaner import cleanup
from gtts import gTTS


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
    print("api rotating")
    new_key = 0 if key == (number_of_api_keys - 1) else key + 1
    print("rotated key from ", key, " to ", new_key)
    return new_key


def generate_video_script(text_data, key):
    openai.api_key = get_key(key)
    prompt = "Give me a short summarised video transcript for this text: " + text_data

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


def generate_keyword(text_data, key):
    openai.api_key = get_key(key)
    prompt = "Give me a keyword describing this piece of text: " + text_data

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
        url = "https://pixabay.com/api/?key=" + pixabay_api_key + "&q=" + key + "&image_type=photo"
        image_result = requests.get(url).json()
        image_url = image_result['hits'][0]['largeImageURL']
        print(image_url)

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


# def get_audios(script_array):
#     for index, scr in enumerate(script_array):
#         url = "https://play.ht/api/v1/convert"
#
#         content = scr
#         payload = {
#             "content": [content],
#             "voice": "en-US-JennyNeural"
#         }
#         headers = {
#             "accept": "application/json",
#             "content-type": "application/json",
#             "AUTHORIZATION": audio_authorisation_key,
#             "X-USER-ID": audio_user_id
#         }
#
#         audio_response = requests.post(url, json=payload, headers=headers)
#         if not audio_response.status_code == 200:
#             cleanup()
#             raise BaseException("Text to Speech API gateway is failing...")
#
#         audio_response = audio_response.json()
#
#         try:
#             transcription_code = audio_response['transcriptionId']
#         except BaseException:
#             print(audio_response)
#             cleanup()
#             raise "audio response is bad"
#
#         url = "https://play.ht/api/v1/articleStatus?transcriptionId=" + transcription_code
#
#         headers = {
#             "accept": "application/json",
#             "AUTHORIZATION": audio_authorisation_key,
#             "X-USER-ID": audio_user_id
#         }
#
#         audio_url_response = requests.get(url, headers=headers).json()
#         print(audio_url_response)
#
#         while not audio_url_response['converted']:
#             time.sleep(10)
#             audio_url_response = requests.get(url, headers=headers).json()
#             print(audio_url_response)
#
#         audio_url = audio_url_response['audioUrl']
#
#         audio_get = requests.get(audio_url)
#
#         if audio_get.status_code:
#             filepath = "Audios/" + str(index) + ".mp3"
#             fp = open(filepath, 'wb')
#             fp.write(audio_get.content)
#             fp.close()


# def main():
#     file_path = "testdoc.pdf"
#     docs = load_pdf_file(file_path)
#     result = custom_prompt(docs)
#     print(result)
#
#
# if __name__ == '__main__':
#     main()


def main():
    current_openai_key = 0
    text, num_pages = extract_pdf('testdoc.pdf')
    script = []
    keyword = []

    for i in range(num_pages):
        script.append(generate_video_script(text[i], current_openai_key))
        keyword.append(generate_keyword(text[i], current_openai_key).split()[0])
        current_openai_key = rotate_key(current_openai_key)
        print(keyword[i])
        # time.sleep(10)  # 10 seconds API cooldown

    get_images(keyword)
    get_audios(script)

    # Video generation
    image_paths, audio_paths = generate_paths('./Images', './Audios')
    merge_image_audio(image_paths, audio_paths, './Videos')
    concat_videos("./Videos")
    cleanup()
    print("Video is successfully produced.")


if __name__ == '__main__':
    main()
