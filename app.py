from flask import Flask, render_template,redirect
import flask
import os
from main import init

app = Flask(__name__)

UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload", methods=['POST'])
def upload():
    if flask.request.method == "POST":
        files = flask.request.files.getlist("file")
        for file in files:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    return render_template("prompt.html")

@app.route("/prompt", methods = ['POST'])
def prompt():
    if flask.request.method == "POST":
        queryText = flask.request.form.get('promptText')

        output = init(queryText)

        return output



@app.route("/", methods = ['GET'])
def home():
    return render_template('index.html')

app.run(debug=True)