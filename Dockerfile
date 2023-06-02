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

ENV PORT 6060
ENV HOST 0.0.0.0
EXPOSE 6060

# Copy the app code into the container
COPY . /app

# Copy restriction policy to ImageMagick
COPY policy.xml /etc/ImageMagick-6/

CMD python worker.py
