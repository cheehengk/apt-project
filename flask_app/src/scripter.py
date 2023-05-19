import sys
import os
import string
import openai
from tenacity import retry, wait_random_exponential
from create_video import merge_image_audio, generate_paths, concat_videos
from keys import openai_rotational_keys, number_of_api_keys
from document_analyser import analyse_doc, extract_pdf
from media_getter import get_images, get_audios
from file_cleaner import cleanup

PARENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Images')
AUDIO_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Audios')
VIDEO_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Videos')
PDF_PATH = os.path.join(PARENT_PATH, 'uploads/user_upload.pdf')


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
    prompt = "Identify an exactly one word descriptive noun which is found or inferred from this piece of text: " + \
             text_data

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": prompt}
        ],
        temperature=0
    )
    output = strip_punctuations(response.choices[0].message.content)
    return output


def main():
    current_openai_key = 0
    print("EXTRACTING PDF......")
    extract_pdf(PDF_PATH)

    print("ANALYZING...")
    script = analyse_doc(current_openai_key)
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
    get_images(keyword)
    print("GENERATING AUDIO...")
    get_audios(script)

    print("CREATING VIDEO...")
    # Video generation
    image_paths = generate_paths('%s' % IMAGE_PATH)
    audio_paths = generate_paths('%s' % AUDIO_PATH)
    merge_image_audio(image_paths, audio_paths, '%s' % VIDEO_PATH, script)
    concat_videos("%s" % VIDEO_PATH)
    cleanup()
    print("Video is successfully produced.")
    return 0


# Process command line arguments
# try:
#     if sys.argv[1].endswith('.pdf'):
#         main(pdf=sys.argv[1])
#     else:
#         raise Exception("Invalid file type, please add .pdf file")
# except IndexError:
#     raise Exception("PLease add .pdf file as argument")

main()