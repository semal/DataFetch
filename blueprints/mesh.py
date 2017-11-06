from flask import Blueprint, render_template, request, redirect, url_for, send_file
from werkzeug import secure_filename
from config import APP_FOLDER
from Controller.get_mesh_code import batch
from Controller.process_mesh_code_result import process

mesh = Blueprint('mesh', __name__, template_folder='%s/templates/mesh' % APP_FOLDER)


@mesh.route('/upload_mesh_phenotypes', methods=['POST'])
def upload_phenotypes():
    print 'Start upload phenotypes file...'
    upload_file = request.files['phenotypes']
    if upload_file:
        print 'Found upload file!'
        filename = secure_filename(upload_file.filename)
        upload_file.save('upload/%s' % filename)
        print 'Saved file!'
        print 'Start get mesh code...'
        batch('upload/%s' % filename)
        print 'Done!'
        process()
        return 'output/mesh_code_result.csv'


@mesh.route('/download_result')
def download_mesh_result():
    return send_file(
        'output/mesh_code_result.csv', as_attachment=True,
        attachment_filename='mesh_code_result.csv'
    )


@mesh.route('/mesh_classifier', methods=['GET'])
def mesh_index():
    return render_template('mesh_index.html')
