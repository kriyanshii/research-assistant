# type: ignore

from flask import Flask, render_template
import flask
import os
from main import Main

app = Flask(__name__)
compute = Main()

UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload", methods=['POST'])
def upload():
    if flask.request.method == "POST":
        files = flask.request.files.getlist("file")
        for file in files:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        try:
            compute.uploadDocuments(app.config['UPLOAD_FOLDER'])
        except:
            return render_template("error.html")

    return render_template("prompt.html")

@app.route("/prompt", methods = ['GET', 'POST'])
def prompt():
    if flask.request.method == "GET":
        return render_template("prompt.html")
    
    if flask.request.method == "POST":
        queryText = flask.request.form.get('promptText')
        try:
            output = compute.query(queryText)
        except:
            return render_template("error.html")
        return render_template("prompt.html", output = output)



@app.route("/", methods = ['GET'])
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
