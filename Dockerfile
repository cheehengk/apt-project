# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
#RUN apt-get update && apt-get install -y redis-server
RUN apt-get update && apt-get install -y ffmpeg

# Copy the requirements file
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt
#RUN apt-get update && apt-get install -y supervisor

# Copy the app code into the container
COPY app.py .
COPY worker.py .
COPY flask_app /app/flask_app
COPY templates /app/templates
COPY google_creds.json /app/google_creds.json
#COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the port that Flask app listens on
EXPOSE 5000

# Set environment variables
ENV REDIS_HOST=redis
ENV GOOGLE_APPLICATION_CREDENTIALS /app/google_creds.json

# Start Redis and run the Flask app
#CMD service redis-server start && python app.py && python worker.py
CMD python app.py && python worker.py
#CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]