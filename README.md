## Convert your PDF documents into informal, educational videos.

### Getting Started
1. Clone the Repo ```git clone https://github.com/cheehengk/ai-playground.git```
2. Move into the directory ```cd ai-playground```
3. Install Requirements ```pip install -r requirements.txt```
4. Copy over secret keys file into the directory: ***flask_app/src***
5. Copy over Google Credentials file into the directory: ***flask_app***
6. Run Redis Server ```redis-server```
7. On another terminal, move into flask_app directory ```cd flask_app```
8. Run worker.py file
9. Run flask app ```GOOGLE_APPLICATION_CREDENTIALS=google_creds.json flask run```
10. App should be running on ```http://127.0.0.1:5000```
