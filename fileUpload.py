import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
import Emotional

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['wav', 'txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/index")
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    anger = []
    surprise = []
    fear = []
    sadness = []
    joy = []
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')   
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print(filename)
            # Emotional.main(filename, 'wav')
            #anger, surprise, fear, sadness, joy = Emotional.main(filename, file.filename.rsplit('.', 1)[1].lower())
            #return render_template('output.html', anger=anger, surprise=surprise, fear=fear, sadness=sadness, joy=joy)
            data1, data2, response = Emotional.main(filename)
            # return render_template('output.html', anger=anger, surprise=surprise, fear=fear, sadness=sadness, joy=joy)
            return render_template('output.html', data1 = data1, data2=data2, response=response)
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
