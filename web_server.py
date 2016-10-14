#!coding:utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, render_template, request, redirect, url_for, send_file
from utils import get_complete_res_by_formula, scrapy_pmid_abstract, insert_formula, \
    insert_abstract, extract_snps, get_formulas, generate_csv_by_formula, search_pubmed

app = Flask(__name__)


@app.route('/')
def formula_search():
    formulas = get_formulas()
    return render_template('formula_search.html', formulas=formulas)


@app.route('/get_result', methods=['POST', 'GET'])
def get_result():
    formula = request.form.get('formula')
    print 'Search pubmed...'
    pmid_list = search_pubmed(formula)
    print 'Got', len(pmid_list), 'from pubmed!'
    res = scrapy_pmid_abstract(pmid_list)
    print res
    if res == 'Got nothing!':
        return redirect(url_for('formula_search'))
    if res == 'Exist!':
        return redirect(url_for('view_pmid_abstract', formula=formula))
    insert_formula(formula)
    insert_abstract()
    return redirect(url_for('view_pmid_abstract', formula=formula))


@app.route('/<formula>')
def view_pmid_abstract(formula):
    records = get_complete_res_by_formula(formula)
    return render_template('pmid_abstract.html', records=records, formula=formula)


@app.route('/extract_snps', methods=['POST'])
def snps_extraction():
    formula = request.form.get('formula')
    extract_snps(formula)
    return redirect(url_for('view_pmid_abstract', formula=formula))


@app.route('/download_snps', methods=['POST'])
def download_snps():
    formula = request.form.get('formula')
    generate_csv_by_formula(formula)
    return send_file(
        'mentioned_snps.csv', as_attachment=True,
        attachment_filename='mentioned_snps.csv'
    )


if __name__ == '__main__':
    app.run(host='192.168.0.11', debug=True, port=1111)
