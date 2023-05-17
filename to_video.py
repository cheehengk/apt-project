import time
import openai
from PyPDF2 import PdfReader
from gtts import gTTS
from mutagen.mp3 import MP3
from PIL import Image
from pathlib import Path
from moviepy import editor
import os

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

def generate_video(input):
    gttsLang = 'en'
    replyObj = gTTS(text=output, lang=gttsLang, slow=False)
    replyObj.save("Recordings/Soundrecording.mp3")
    collect_path = '.../aitest/ai_playground1'
    audio_path = "Recordings/Soundrecording.mp3"
    video_path = "Recordings/Videoproduct.mp4"
    folder_path = ".../aitest/ai_playground1/Recordings"
    full_audio_path = os.path.join(collect_path, audio_path)
    full_video_path = os.path.join(collect_path, video_path)

    voice = MP3(audio_path)
    audio_length= round(voice.info.length)
    audio_length

    path_images = Path(folder_path)

    images = list(path_images.glob('*.jpg'))

    image_list = list()

    for image_name in images:
        image = Image.open(image_name).resize((800, 800), Image.ANTIALIAS)
        image_list.append(image)

    total_time = int(audio_length/len(image_list)) * 1000
    print(total_time)

    image_list[0].save(os.path.join(folder_path, "temp.gif"),
                       save_all=True,
                       append_images=image_list[1:],
                       duration=total_time)
    
    audio = editor.AudioClip(full_audio_path)
    print("Audio complete")

    video = editor.VideoFileClip(os.path.join(folder_path, "temp.gif"))
    print("video complete")

    final_product = video.set_audio(audio)

    final_product.write_videofile(full_video_path)

    return final_product


# Main Program Here
file_path = "testdoc.pdf"
text, num_pages = extract_pdf(file_path)
script = []

for i in range(num_pages):
    print("Page ", i + 1)
    script.append(generate_video_script(text[i]))
    # time.sleep(3)  # 3 seconds delay to cool down API calls

generate_video(script)
