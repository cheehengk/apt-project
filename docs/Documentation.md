# APT-Mini-Project: Convert your PDF documents into informal, educational videos

## Project Description
Project involves converting PDF documents into concise education (slide-show based) videos. 
Usage of OpenAI API for summarising PDF content. Video produced using Google Text-to-Speech, royalty-free images from Pixabay and MoviePy for editing.

Request link to live deployment from repository owner.

---
## Getting Started
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
## Under the Hood
### Architecture
In general, the application follows a Client-Server architecture (Docker) and partly Event-Driven architecture (Redis Queue).
<img src=static/architecture.jpeg width="400" height="400">

### Sequence Diagram
<img src=static/ai-video-generation.png width="653" height="636" alt="">

### Video Maker
1. Extract PDF and break into 5-pages sized chunks.
2. Analyze the chunks with LangChain `AnalyzeDocumentChain` and generate summary of each chunk.
3. Cut each chunk into 10 words slices and save them as local assets for subtitling.
4. Generate a single descriptive keyword for each slice with OpenAI `ChatCompletion`.
5. For each keyword, search for relevant image on Pixabay and save as local assets.
6. Generate audio with Google Text-to-Speech for each slice and save as local assets.
7. Merge images to corresponding audio files to create video. Overlay with subtitles and save as local assets.
8. Concatenate videos to generate final product. Clean up local store.
---
## Developer's Journal
### Video Maker
What started out as an attempt to experi with the OpenAI API turned into a mini side project for converting a PDF document into an educational video. The plan for video maker was drafted out early on and was roughly followed through other than how images were procured. The original idea was to use generative AI to ensure the accuracy and relevance of each image to what was discussed in a particular text slice. However, due to the low limit of free tiers on various public models, and the sheer number of requests required per video, it was switched to a free and unlimited option: Pixabay image library.

At the beginning, LangChain's Document Analyzer Chain (DAC) was not used. The original approach involves generating a summary for each page of PDF content with OpenAI ChatCompletion. The result was inconsistent, with pages which are low in word count, or in the extreme case of a blank page, generating garbage summaries. Since switching to DAC, the results are more consistent.

Five-page chunks were used due to the token limit. If excess content was posted to the API, the result was unpredictable and useless, or it will result in an error. 10 words slices was decided on the basis of readable subtitles and sufficient dynamism in the final video. ChatCompletion was used for keyword generation due to its simplicity as compared to more complex LangChain chains.

As the design decision for image generation has already been covered, I will move on to discuss on audio generation. The first instinct was to use generative AI for text-to-speech. Similar to the constraints of AI image generation, the approach was dropped. Google Text-to-Speech (gTTS) was adopted instead, albeit the lower quality output; audio are not always completely accurate. For future projects involving text-to-speech, a separate voice model can be trained to replicate a real life person or celebrity.

MoviePy was the obvious option for video editing. The project was already largely coded in Python and the library was simple to use. Some difficulties with export codec and aspect ratios was faced. The final output was still flawed but the issue was not delved into once quality was somewhat satisfactory.

### Backend Development
Backend development begun with the idea of a simple upload and convert design. New ideas were introduced along the way, prompting for a more complex backend setup. Flask was used to develop the web application and API. Development was rather smooth until the issue of background job was posed. On top of rendering an HTML response, there was a need to run a long background job (making the video). To resolve the issue, Redis Queue (RQ) was implemented, with a Redis server acting as the broker for task requests and a Worker to handle the video generation.

Two databases were planned to be used from the beginning, a cloud storage bucket (Google Cloud Storage) and a relational database (MySQL) to log the task tickets. The initial approach was to let the Flask app handle all the communication with the databases, with a temporary local storage acting as the intermediary between itself and the Worker. However, nearer to deployment, it was realised that the Worker had to be deployed as an independent module. The design was changed to one where PDF and Video assets are posted to the storage bucket and requested for by the other party.

### Deployment
Deployment proved to be the most tedious and bothersome part of this project. It was decided early on to dockerize the application and host the container somewhere. As mentioned in the previous section, the Worker and redis server had to be run on separate containers, which posed major issues to deployment. Eventually, Docker Compose was used to manage the multi-container application. The general idea was to use GitHub actions to automate the build process and deploy onto Google Cloud Run (GCR).

During deployment to GCR, many issues were faced. Firstly, Docker Compose did not work as expected and was used only for local development and testing. The workflow had to deploy each of the three containers separately. This resulted in listening port issues, even when the container port matches that of the service settings. The closest to full live deployment attempt only had the Flask-App container running, but not the Worker and Redis server. There was significant effort and time spent on trying to deploy on GCR, but to no avail.

Eventually, to simplify the issue and eliminate the problem with hosts and ports, the three services were entirely individualised. The Flask-App and Worker were built separately with different Dockerfiles (although the settings and dependencies are largely the same) resulting in two Docker images. The images were pushed to Google Cloud Container Registry. The imagesThe Redis server is currently running on RedisLabs on a free tier, with future migration to Upstash considered.

A Virtual Machine (VM) was set up on Google Cloud Compute Engine with Docker and Dokku (PaaS) installed. From there, the images were pulled from the Google registry and deployed. One key issue faced here, and also a valuable learning point, was the need to set up an additional firewall rule for the deployed Dokku apps to be accessed via the VM's iP.

This manual way of deployment was overall unsatisfactory, as any changes pushed onto the repository's main branch will not be automatically tested (if any tests), integrated, and deployed. In this sense, CI/CD was not complete. Dokku, however, does support Git-based deployment, which can be explored in the future.

## Screenshot of Deployment
<img src=static/deployment-screenshot.png alt="">