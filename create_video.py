import os

from moviepy.editor import AudioFileClip, ImageClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip


def merge_image_audio(image_array, audio_array, output_path):
    if not len(image_array) == len(audio_array):
        raise Exception("Number of images and audio files does not match!")

    for index in range(len(image_array)):
        audio_clip = AudioFileClip(audio_array[index])
        image_clip = ImageClip(image_array[index])
        video_clip = image_clip.set_audio(audio_clip)
        video_clip.duration = audio_clip.duration
        filepath = output_path + "/" + str(index) + ".mp4"
        open(filepath, 'wb')
        video_clip.write_videofile(filepath, fps=1, threads=1, codec="libx264")


def generate_paths(image_path, audio_path):
    image_path_array = []
    audio_path_array = []

    # Loop through each file in the directory
    for image_filename in os.listdir(image_path):
        # Construct the full file path by joining the directory path and filename
        file_path = os.path.join(image_path, image_filename)

        # Check if the file path is a file (not a subdirectory)
        if os.path.isfile(file_path):
            image_path_array.append(file_path)

# Loop through each file in the directory
    for audio_filename in os.listdir(audio_path):
        # Construct the full file path by joining the directory path and filename
        file_path = os.path.join(audio_path, audio_filename)

        # Check if the file path is a file (not a subdirectory)
        if os.path.isfile(file_path):
            audio_path_array.append(file_path)

    return image_path_array, audio_path_array


def concat_videos(video_path):
    video_path_array = []
    for image_filename in os.listdir(video_path):
        # Construct the full file path by joining the directory path and filename
        if image_filename == ".DS_Store":
            pass
        else:
            file_path = os.path.join(video_path, image_filename)
            if os.path.isfile(file_path):
                video_path_array.append(file_path)

    print(video_path_array)

    clips = []
    for index, clip in enumerate(video_path_array):
        clips.append(VideoFileClip(clip))

    movie = concatenate_videoclips(clips)

    filepath = "./movie.mp4"
    open(filepath, 'wb')
    movie.write_videofile(filepath, fps=1, threads=1, codec="libx264")
