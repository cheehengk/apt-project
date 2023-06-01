import requests
import os
from gtts import gTTS
from random import randint

PARENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
IMAGE_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Images')
AUDIO_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Audios')


def get_images(keyword_array, pixabay_api_key):
    for index, key in enumerate(keyword_array):
        url = "https://pixabay.com/api/?key=" + pixabay_api_key + "&q=" + key + "&image_type=photo"
        image_result = requests.get(url).json()

        response = image_result.get('hits', [])
        if len(response):
            rand = randint(0, 2)
            try:
                image_url = response[rand]['largeImageURL']
            except IndexError:
                image_url = "https://pixabay.com/get" \
                            "/gd2c344ba85997dade4022a2421b67ea1eb0e5b25dfb6bb41dba4fb23fab8d81626f2f349dc7f946aea9758ae354358cd22f1dfa8fd1c8e3f1f2d1f425733ef5a_1280.jpg"
        else:
            image_url = "https://pixabay.com/get" \
                        "/gd2c344ba85997dade4022a2421b67ea1eb0e5b25dfb6bb41dba4fb23fab8d81626f2f349dc7f946aea9758ae354358cd22f1dfa8fd1c8e3f1f2d1f425733ef5a_1280.jpg"

        image_response = requests.get(image_url)

        print(image_response)
        if image_response.status_code:
            filepath = IMAGE_PATH + "/" + str(index) + ".jpg"
            fp = open(filepath, 'wb')
            fp.write(image_response.content)
            fp.close()


def get_audios(script_array):
    for index, scr in enumerate(script_array):
        speech = gTTS(scr)
        filepath = AUDIO_PATH + "/" + str(index) + ".mp3"
        speech.save(filepath)
