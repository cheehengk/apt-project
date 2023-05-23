import datetime
import os
import shutil
from datetime import timedelta
from random import randint

from redis import Redis
from rq import Queue
from flask import Flask, render_template, make_response, redirect, request
from werkzeug.utils import secure_filename
from google.cloud import storage
from flask_app.src.scripter import main
import mysql.connector
from flask_app.src.keys import sql_host, sql_database, sql_password, sql_user
from blinker import signal

RQ_FINISHED_STATUS = 'finished'
UPLOAD_FOLDER = 'local_store'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 1000000  # in bytes

# DO NOT CHANGE!!!
GCS_BUCKET = "ai-proj"
PDF_FOLDER = "PDFs"
VIDEO_FOLDER = "VIDEOs"


# DO NOT CHANGE!!!

def create_sql_connection():
    print("establishing sql connection")
    cnx = mysql.connector.connect(
        user=sql_user,
        password=sql_password,
        host=sql_host,
        database=sql_database
    )
    cursor = cnx.cursor()
    print("sql connection established")
    return cnx, cursor


update_query = "UPDATE data SET VIDEO_URL = %s, CONVERSION_TASK_ID = %s, TIME_COMPLETED = %s, STATUS = %s WHERE " \
               "ID = %s"
insert_query = "INSERT INTO data ( PDF_URL, VIDEO_URL, CONVERSION_TASK_ID, TIME_CREATED, TIME_COMPLETED, STATUS) " \
               "VALUES ( %s, %s, %s, %s, %s, %s)"
# for postgres syntax
# ON CONFLICT (unique_1, unique_2) UPDATE tb_name set other_field_1=value, other_field_2=value_2
# ON CONFLICT (unique_1, unique_2) DO NOTHING -> ignore the insertion

# Flask Signal

sql_insertion_signal = signal('sql_insertion')

# Redis Queue
redis_conn = Redis()
q = Queue(connection=redis_conn)

if __name__ == '__main__':
    app.run()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_local_store():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def upload_to_gcs(bucket_name, local_file_path, req_id, upload_type):
    FOLDER = PDF_FOLDER if upload_type == 0 else VIDEO_FOLDER
    EXT = '.pdf' if upload_type == 0 else '.mp4'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(FOLDER + '/' + str(req_id) + EXT)
    blob.upload_from_filename(local_file_path)
    url = blob.generate_signed_url(expiration=timedelta(hours=2), method="GET")
    return url


def upload_initial_sql_data(pdf_gcs_url):
    cnx, cursor = create_sql_connection()
    sql_data = [
        (pdf_gcs_url, None, None, str(datetime.datetime.now()), None, 'RECEIVED')
    ]
    print("executing")
    cursor.executemany(insert_query, sql_data)
    cursor.execute("SELECT LAST_INSERT_ID()")
    primary_key = cursor.fetchone()[0]
    print(primary_key)
    cnx.commit()

    if cursor.rowcount == 0:
        cursor.close()
        cnx.close()
        return 0

    cursor.close()
    cnx.close()
    return primary_key


def update_sql_data(pkey, video_gcs_url, conversion_task_id):
    cnx, cursor = create_sql_connection()
    data = (video_gcs_url, conversion_task_id, str(datetime.datetime.now()), 'COMPLETED', int(pkey))
    cursor.execute(update_query, data)
    cnx.commit()

    if cursor.rowcount == 0:
        cursor.close()
        cnx.close()
        return False

    cursor.close()
    cnx.close()
    return True


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
    f = request.files['file']
    if f and allowed_file(f.filename):
        req_id = random_with_N_digits(10)
        f.filename = 'user_upload.pdf'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        f.save(file_path)
        # return redirect('/run')

        pdf_gcs_url = upload_to_gcs(GCS_BUCKET, file_path, req_id, 0)  # upload_type = 0 for PDF

        if pdf_gcs_url is not None:
            print('upload_sql')
            pkey = upload_initial_sql_data(pdf_gcs_url)
            if not pkey == 0:
                sql_insertion_signal.send([req_id, pkey])
                return "Successful insertion"
            else:
                return "sql insertion failure!"
        else:
            return "bucket upload error!"

    else:
        return redirect('/error/invalid-file-type')


def run(details):
    req_id = details[0]
    pkey = details[1]
    task = q.enqueue(main)
    while not task.get_status() == RQ_FINISHED_STATUS:
        print("PROCESSING")

    # Uploading mp4 to Google Cloud Buckets
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_video.mp4')
    video_gcs_url = upload_to_gcs(GCS_BUCKET, file_path, req_id, 1)

    if update_sql_data(pkey, video_gcs_url, str(task.id)):
        print(video_gcs_url)

    cleanup_local_store()


sql_insertion_signal.connect(run)
