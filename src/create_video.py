import os

from moviepy.editor import AudioFileClip, ImageClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip


def get_img_aud_rank(filename):
    filename = filename[10:]
    filename = filename[:-4]
    return int(filename)


def get_txt_rank(filename):
    filename = filename[9:]
    filename = filename[:-4]
    return int(filename)


def merge_image_audio(image_array, audio_array, output_path, script):
    if not len(image_array) == len(audio_array):
        raise Exception("Number of images and audio files do not match!")
    if not len(image_array) == len(script):
        raise Exception("Number of images and script lines do not match!")

    image_array.sort(key=get_img_aud_rank)
    audio_array.sort(key=get_img_aud_rank)
    print(image_array)
    print(audio_array)

    for index in range(len(image_array)):
        audio_clip = AudioFileClip(audio_array[index])
        image_clip = resize(ImageClip(image_array[index]), width=1980, height=1080)
        video_clip = image_clip.set_audio(audio_clip)
        video_clip.duration = audio_clip.duration

        subtitle_text = script[index]
        subtitle = TextClip(subtitle_text, fontsize=30, color="white", bg_color="black", kerning=-1)
        subtitle = subtitle.set_duration(video_clip.duration)
        subtitle = subtitle.set_position(("center", "bottom"))
        video_with_subtitle = CompositeVideoClip([video_clip, subtitle])
        video_with_subtitle.duration = audio_clip.duration

        filepath = output_path + "/" + str(index) + ".mp4"
        open(filepath, 'wb')
        video_with_subtitle.write_videofile(filepath, fps=1, threads=1, codec="libx264")


def generate_paths(path):
    path_array = []

    # Loop through each file in the directory
    for image_filename in os.listdir(path):
        # Construct the full file path by joining the directory path and filename
        file_path = os.path.join(path, image_filename)

        # Check if the file path is a file (not a subdirectory)
        if os.path.isfile(file_path):
            path_array.append(file_path)

    return path_array


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

    video_path_array.sort(key=get_img_aud_rank)
    print(video_path_array)

    clips = []
    count = 0
    for index, clip in enumerate(video_path_array):
        clips.append(VideoFileClip(clip))
        count += 1

    movie = concatenate_videoclips(clips, method='compose')

    filepath = "../movie.mp4"
    open(filepath, 'wb')
    movie.write_videofile(filepath, fps=1, threads=1, codec="libx264")

# script = ["okk", "okk", "okk", "okk", "okk",
#           "okk", "okk", "okk", "okk", "okk",
#           "okk", "okk", "okk", "okk", "okk"]
#
# image_paths, audio_paths = generate_paths('./Images', './Audios')
# merge_image_audio(image_paths, audio_paths, './Videos', script)
# concat_videos("./Videos")
