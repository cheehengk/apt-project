import os
import shutil

PARENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
IMAGE_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Images')
AUDIO_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Audios')
VIDEO_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Videos')
TEXT_PATH = os.path.join(PARENT_PATH, 'src/temp_assets/Texts')


def clean_images():
    for filename in os.listdir(IMAGE_PATH):
        file_path = os.path.join(IMAGE_PATH, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def clean_audios():
    for filename in os.listdir(AUDIO_PATH):
        file_path = os.path.join(AUDIO_PATH, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def clean_videos():
    for filename in os.listdir(VIDEO_PATH):
        file_path = os.path.join(VIDEO_PATH, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def clean_texts():
    for filename in os.listdir(TEXT_PATH):
        file_path = os.path.join(TEXT_PATH, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def cleanup():
    clean_images()
    clean_audios()
    clean_videos()
    clean_texts()
    print("Intermediary assets cleaned up.")

# cleanup()
