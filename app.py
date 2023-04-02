# type: ignore

from flask import Flask, render_template
import flask
import os
from remote import Remote

app = Flask(__name__)
compute = Remote()

UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload", methods=['POST'])
def upload():
    if flask.request.method == "POST":
        exceeded_size = False
        files = flask.request.files.getlist("file")
        for file in files[:5]:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            file_size = os.stat(path).st_size
            #For 5MB max file size, 1024*1024*5
            if file_size > 5242880:
                exceeded_size = True
                os.remove(path)
        try:
            compute.uploadDocuments(app.config['UPLOAD_FOLDER'])
        except Exception as err:
            print(f'Error while executing completion query: {err}')
            return render_template("error.html")
    if exceeded_size:
        return render_template("prompt.html", output="You have exceeded either the file size or number limits")
    else:
        return render_template("prompt.html")

@app.route("/prompt", methods = ['GET', 'POST'])
def prompt():
    if flask.request.method == "GET":
        return render_template("prompt.html")
    
    if flask.request.method == "POST":
        queryText = flask.request.form.get('promptText')
        try:
            prompt, output, references = compute.query(queryText)
        except Exception as err:
            print(f'Error while executing completion query: {err}')
            return render_template("error.html")
        return render_template("prompt.html", output=output, prompt=prompt.split('\n'), references=references)



@app.route("/", methods = ['GET'])
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
