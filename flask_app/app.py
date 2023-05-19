import os
import src.scripter
from flask import Flask, render_template, make_response, request, redirect
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 1000000  # in bytes


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

            return 'file uploaded successfully'
        else:
            return redirect('/error/invalid-file-type')


def ai_conversion():
    print('loading')
    dir_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    file_count = 0
    # Iterate directory
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            file_count += 1

    if not file_count == 1:
        return redirect('/error/file-count-error')

    # AI Conversion here
    response = 0

    if not response == 0:
        return redirect('/error/conversion-failure')

    assert response == 0

    return redirect('/complete')


@app.route('/complete')
def complete():
    return 'complete!'
