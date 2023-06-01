## Convert your PDF documents into informal, educational videos.

### Project Description

Project involves converting PDF documents into concise education (slide-show based) videos. 
Usage of OpenAI API for summarising PDF content. Video produced using Google Text-to-Speech, royalty-free images from Pixabay and MoviePy for editing.
---
### Getting Started
1. Clone the Repo ```git clone https://github.com/cheehengk/ai-playground.git```
2. Move into the directory ```cd ai-playground```
3. Install Requirements ```pip install -r requirements.txt```
4. Copy over secret keys file into root directory
5. Copy over Google Credentials file into root directory

*Running on Terminal*
1. Run worker.py file ```python worker.py```
2. Run flask app ```GOOGLE_APPLICATION_CREDENTIALS=google_creds.json flask run```

*Docker*
1. Install Docker Daemon
2. Run ```docker-compose up```
    
App should be running on ```http://127.0.0.1:5000```

---
Contact repository owner for link to live deployment and required resources for local testing. 