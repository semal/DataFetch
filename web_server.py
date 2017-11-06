#!coding:utf-8
import sys
from config import APP_FOLDER

sys.path.insert(0, APP_FOLDER)
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, render_template
from blueprints.pubmed import pubmed
from blueprints.mesh import mesh

app = Flask(__name__)
app.register_blueprint(pubmed)
app.register_blueprint(mesh)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='192.168.0.11', debug=True, port=1111, threaded=False)
