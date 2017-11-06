#!coding:utf-8
import sys
from config import APP_FOLDER

sys.path.insert(0, APP_FOLDER)
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, render_template, request, send_file
from blueprints.pubmed import pubmed
from blueprints.mesh import mesh
from Controller.get_transcripts import get_transcripts

app = Flask(__name__)
app.register_blueprint(pubmed)
app.register_blueprint(mesh)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download-transcripts')
def download_transcripts():
    return render_template('download-transcripts.html')


@app.route('/get-transcripts', methods=['POST'])
def get_transcripts_sequence():
    accessions = [e.strip() for e in request.form.get('accessions').split('\n') if e.strip() != '']
    sequence = get_transcripts(accessions)
    with open('res.fq', 'w') as fo:
        fo.write(sequence)
    return send_file('res.fq', as_attachment=True, attachment_filename='result.fq')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080, threaded=False)
