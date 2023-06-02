import datetime
import os
import shutil
import time
from datetime import timedelta
from random import randint
from PyPDF2 import PdfReader
from rq import Queue
from flask import Flask, render_template, make_response, request
from werkzeug.utils import secure_filename
from google.cloud import storage
import mysql.connector
from blinker import signal
from flask_socketio import SocketIO, emit, Namespace
from dotenv import load_dotenv
from redis import Redis

load_dotenv()
sql_host = os.getenv("SQL_HOST")
sql_database = os.getenv("SQL_DATABASE")
sql_user = os.getenv("SQL_USER")
sql_password = os.getenv("SQL_PW")
socket_io_key = os.getenv("SOCKETIO_KEY")
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_pw = os.getenv("REDIS_PW")

RQ_FINISHED_STATUS = 'finished'
RQ_FAILED_STATUS = 'failed'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['MAX_CONTENT_PATH'] = 1000000  # in bytes

# SocketIO
app.config['SECRET_KEY'] = socket_io_key
socketio = SocketIO(app)
signal_namespace = Namespace()

# DO NOT CHANGE!!!
GCS_BUCKET = "artifacts.apt-ai-project.appspot.com"
PDF_FOLDER = "PDFs"
VIDEO_FOLDER = "VIDEOs"
# DO NOT CHANGE!!!

# Flask Signal

sql_insertion_signal = signal('sql_insertion')

redis_conn = Redis(
        host=redis_host,
        port=int(redis_port),
        password=redis_pw
)
q = Queue(connection=redis_conn)

wait_messages = [
    "Please wait while we process your request.",
    "We are working on it. Please hold on.",
    "The process may take a moment. Thank you for your patience.",
    "Sit tight! We're processing your data.",
    "Just a moment, we're almost done.",
    "Hang in there while we complete the task.",
    "Please be patient while we finish the process.",
    "We're crunching the numbers. Please wait.",
    "Processing in progress. Your patience is appreciated.",
    "Stay tuned! We'll be done shortly."
]

global_url_returned = None

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


def allowed_file(file):
    filename = file.filename
    extension_check = '.' in filename and \
                      filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    # if not extension_check:
    #     return False
    #
    # try:
    #     pdf = PdfReader(file)
    #     page_count = len(pdf.pages)
    # except Exception as e:
    #     print('Cannot read file. Reason: %s' % e)
    #     return False
    #
    # if page_count > 15:
    #     return False

    return extension_check


# def cleanup_local_store():
#     for filename in os.listdir(UPLOAD_FOLDER):
#         file_path = os.path.join(UPLOAD_FOLDER, filename)
#         try:
#             if os.path.isfile(file_path) or os.path.islink(file_path):
#                 os.unlink(file_path)
#             elif os.path.isdir(file_path):
#                 shutil.rmtree(file_path)
#         except Exception as e:
#             print('Failed to delete %s. Reason: %s' % (file_path, e))


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def upload_to_gcs(bucket_name, file, req_id):
    FOLDER = PDF_FOLDER
    EXT = '.pdf'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(FOLDER + '/' + str(req_id) + EXT)
    blob.upload_from_file(file)
    url = blob.generate_signed_url(expiration=timedelta(days=7), method="GET")
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
    else:
        err = 'Error!'

    return make_response(render_template('index.html', message=err))


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    socketio.emit('reading-file', {'message': 'Reading your file...'})
    f = request.files['file']
    if f and allowed_file(f):
        req_id = random_with_N_digits(10)
        # f.filename = 'user_upload.pdf'
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        # f.save(file_path)

        pdf_gcs_url = upload_to_gcs(GCS_BUCKET, f, req_id)  # upload_type = 0 for PDF

        if pdf_gcs_url is not None:
            print('upload_sql')
            pkey = upload_initial_sql_data(pdf_gcs_url)
            if not pkey == 0:
                sql_insertion_signal.send([req_id, pkey, pdf_gcs_url])
                return global_url_returned
            else:
                socketio.emit('error', {'message': 'SQL Insertion Error, please try again later!'})
                return "sql-insertion-failure"
        else:
            socketio.emit('error', {'message': 'Bucket Upload Error, please try again later!'})
            return "bucket-upload-error"

    else:
        socketio.emit('error', {'message': 'Incorrect file type, or PDF file is too large, limit to 15 pages!'})
        return "invalid-file!"


@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to the server'})


def random_message():
    return wait_messages[randint(0, 9)]


def run(details):
    req_id = details[0]
    pkey = details[1]
    pdf_url = details[2]
    task = q.enqueue('flask_app.src.scripter.main', [pdf_url, req_id])
    while not task.get_status() == RQ_FINISHED_STATUS:
        if task.get_status() == RQ_FAILED_STATUS:
            exception = task.exc_info  # Get the exception details
            error_message = str(exception[1]) if exception else 'Unknown error'
            print(error_message)
            socketio.emit('error', {'message': 'Conversion job failed!'})
            return "conversion-job-failure"
        time.sleep(10)
        socketio.emit('conversion-message', {'message': random_message()})

    video_gcs_url = task.result

    if video_gcs_url is not None:
        if update_sql_data(pkey, video_gcs_url, str(task.id)):
            socketio.emit('success', {'message': video_gcs_url})
            global global_url_returned
            global_url_returned = video_gcs_url
            return video_gcs_url
        else:
            socketio.emit('error', {'message': 'SQL Insertion Error, please try again later!'})
            return "sql-insertion-failure"
    else:
        socketio.emit('error', {'message': 'Bucket Upload Error, please try again later!'})
        return "bucket-upload-error!"


sql_insertion_signal.connect(run)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
