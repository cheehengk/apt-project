import os
import string
import openai
import requests
from tenacity import retry, wait_random_exponential
from dotenv import load_dotenv
from flask_app.src.processor.create_video import generate_paths, merge_image_audio, concat_videos
from flask_app.src.llm.document_analyser import extract_pdf, analyse_doc
from flask_app.src.processor.file_cleaner import cleanup
from flask_app.src.processor.media_getter import get_images, get_audios

PARENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Images')
AUDIO_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Audios')
VIDEO_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Videos')
ENV_PATH = os.path.join(PARENT_PATH, '..')

load_dotenv()
openai_rotational_keys = [os.getenv('OPENAI_KEY_1')]
pixabay_api_key = os.getenv('PIXABAY_API_KEY')
number_of_api_keys = 1


def get_key(key):
    return openai_rotational_keys[key]


def rotate_key(key):
    new_key = 0 if key == (number_of_api_keys - 1) else key + 1
    return new_key


def strip_punctuations(text):
    # Remove starting punctuations
    while text and text[0] in string.punctuation:
        text = text[1:]

    # Remove ending punctuations
    while text and text[-1] in string.punctuation:
        text = text[:-1]

    return text


@retry(wait=wait_random_exponential(min=1, max=60))
def generate_keyword(text_data, key):
    openai.api_key = get_key(key)
    prompt = "Identify an exactly one word descriptive noun, longer than 3 letters, which is found or inferred from " \
             "this piece of text: " + \
             text_data

    response = openai.Completion.create(
        model="text-davinci-003",
        # messages=[
        #     {"role": "user",
        #      "content": input_prompt}
        # ],
        prompt=prompt,
        temperature=0
    )
    output = strip_punctuations(response.choices[0].text)
    return output


def download_pdf_payload(url):
    response = requests.get(url)
    return response.content


def main(payload):
    pdf_url = payload[0]
    req_id = payload[1]
    file = download_pdf_payload(pdf_url)
    current_openai_key = 0
    print("EXTRACTING PDF......")
    extract_pdf(file)

    print("ANALYZING...")
    script = analyse_doc(get_key(current_openai_key))
    current_openai_key = rotate_key(current_openai_key)

    script_length = len(script)
    print("Number of Scenes: ", script_length)

    keyword = []

    for j in range(script_length):
        keyword.append(generate_keyword(script[j], current_openai_key).split()[0])
        current_openai_key = rotate_key(current_openai_key)
        print("Scene ", j + 1, "/", script_length, " keyword: ", keyword[j])
        # time.sleep(10)

    print("GETTING IMAGES...")
    get_images(keyword, pixabay_api_key)
    print("GENERATING AUDIO...")
    get_audios(script)

    print("CREATING VIDEO...")
    # Video generation
    image_paths = generate_paths('%s' % IMAGE_PATH)
    audio_paths = generate_paths('%s' % AUDIO_PATH)
    merge_image_audio(image_paths, audio_paths, VIDEO_PATH, script)
    url = concat_videos(VIDEO_PATH, req_id)
    cleanup()
    print("Video is successfully produced.")
    return url


# Process command line arguments
# try:
#     if sys.argv[1].endswith('.pdf'):
#         main(pdf=sys.argv[1])
#     else:
#         raise Exception("Invalid file type, please add .pdf file")
# except IndexError:
#     raise Exception("PLease add .pdf file as argument")
#
# if __name__ == '__main__':
#     main()
