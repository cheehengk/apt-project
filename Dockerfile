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

ENV FLASK_RUN_HOST 0.0.0.0
ENV PORT 5000
EXPOSE 5000

# Copy the app code into the container
COPY . /app

# Copy restriction policy to ImageMagick
COPY policy.xml /etc/ImageMagick-6/

CMD ["echo", "This is a placeholder command"]
