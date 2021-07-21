from flask import Flask, render_template, request, flash, redirect, session
from werkzeug.utils import secure_filename
import os
from uuid import uuid4

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['UPLOAD_FOLDER'] = os.environ['UPLOAD_FOLDER']
app.secret_key = 'AVVCDF654#@'
ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template("home.html")
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Sem arquivo!')
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            session['id'] = uuid4()
            filename = secure_filename(file.filename)
            fname_split = filename.split('.')
            fname_id = fname_split[0] + '-' + str(session['id']) + '.' + fname_split[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname_id))
            return render_template('file_data.html', data={'filename': fname_id})
        else:
            flash('Extensão de arquivo inválida!')
            return redirect(request.url)


if __name__ == '__main__':
    app.run()
