# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
#RUN apt-get update && apt-get install -y redis-server
RUN apt-get update && apt-get install -y ffmpeg libavcodec-extra
RUN apt-get update && apt-get install -y imagemagick

# Copy the requirements file
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt
#RUN apt-get update && apt-get install -y supervisor

ENV PORT 5050
ENV HOST 0.0.0.0
EXPOSE 5050

# Copy the app code into the container
COPY . .
# Prepare all folders
RUN mkdir -p flask_app/src/temp_assets/Audios
RUN mkdir -p flask_app/src/temp_assets/Videos
RUN mkdir -p flask_app/src/temp_assets/Images
RUN mkdir -p flask_app/src/temp_assets/Texts
RUN mkdir -p flask_app/local_video_store
# Copy restriction policy to ImageMagick
COPY policy.xml /etc/ImageMagick-6/

CMD python app.py
