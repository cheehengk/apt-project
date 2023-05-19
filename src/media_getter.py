import requests
from gtts import gTTS
from random import randint
from keys import pixabay_api_key


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
                image_url = "https://pixabay.com/get" \
                            "/gcfcafd5ec3dc85b8b24b0da96ec1b54b078ee9e9a07aefee345f7d885bf5228f15b848036c51797d6" \
                            "d9313e24faeb4972c3d796595133ad3541936b991568d5b_1280.jpg"
        else:
            image_url = "https://pixabay.com/get" \
                        "/gcfcafd5ec3dc85b8b24b0da96ec1b54b078ee9e9a07aefee345f7d885bf5228f15b848036c51797d6d931" \
                        "3e24faeb4972c3d796595133ad3541936b991568d5b_1280.jpg"

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
