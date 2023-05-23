import os
import time
from redis import Redis
from rq import Queue
from rq.job import Job
from flask import Flask, render_template, make_response, redirect, request
from werkzeug.utils import secure_filename
from google.cloud import storage

from flask_app.src.scripter import main

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 1000000  # in bytes

# DO NOT CHANGE!!!
GCS_BUCKET = "ai-proj"
PDF_FOLDER = "PDFs"
VIDEO_FOLDER = "VIDEOs"
# DO NOT CHANGE!!!

redis_conn = Redis()
q = Queue(connection=redis_conn)

if __name__ == '__main__':
    app.run()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/gcs')
# def gcs():
#     result = upload_pdf_to_gcs('ai-pdf', '../requirements.txt', 'ehfe/dbcd')
#     return result


def upload_pdf_to_gcs(bucket_name, local_file_path, id):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(id + '.pdf')
    blob.upload_from_filename(local_file_path)
    url = blob.generate_signed_url(expiration=timedelta(days=7), method="GET")
    return url


@app.route('/')
def index():
    return make_response(render_template('index.html', response=''))


@app.route('/error/<err>')
def error(err):
    if err == 'invalid-file-type':
        err = 'Invalid File Type!'
    elif err == 'file-count-error':
        err = 'Wrong number of files in upload directory!'
    elif err == 'conversion-failure':
        err = 'Conversion failure!'
    else:
        err = 'Error!'

    return make_response(render_template('index.html', message=err))


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            f.filename = 'user_upload.pdf'
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            # return redirect('/run')

            pdf_gcs_url = upload_pdf_to_gcs(GCS_BUCKET, )
            # create new entry in db with pdf url

        else:
            return redirect('/error/invalid-file-type')


@app.route('/run', methods=['GET', 'POST'])  # run when db is updated, UPDATE to only POST
def run():
    if request.method == "POST" or request.method == "GET":
        job = q.enqueue(main)
        print(job.get_status())
        return redirect('/results/' + str(job.id))
    else:
        return request.method


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    print("JOB KEY", job_key)
    job = Job.fetch(job_key, connection=redis_conn)
    while not job.is_finished:
        print("processing")
        time.sleep(15)

    return "Success!"
