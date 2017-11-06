from flask import Blueprint, render_template, request, redirect, url_for, send_file
from Controller.pubmed_controller import get_formulas, search_pubmed, scrapy_pmid_abstract, \
    insert_formula, insert_abstract, get_complete_res_by_formula, extract_snps, \
    generate_csv_by_formula
from config import APP_FOLDER

pubmed = Blueprint('pubmed', __name__, template_folder='%s/templates/pubmed' % APP_FOLDER)


@pubmed.route('/pubmed_search')
def formula_search():
    formulas = get_formulas()
    return render_template('formula_search.html', formulas=formulas)


@pubmed.route('/get_result', methods=['POST', 'GET'])
def get_result():
    formula = request.form.get('formula')
    print 'Search pubmed...'
    pmid_list = search_pubmed(formula)
    print 'Got', len(pmid_list), 'from pubmed!'
    res = scrapy_pmid_abstract(pmid_list)
    print res
    if res == 'Got nothing!':
        return redirect(url_for('pubmed.formula_search'))
    if res == 'Exist!':
        return redirect(url_for('pubmed.view_pmid_abstract', formula=formula))
    print 'Insert formula...'
    insert_formula(formula)
    print 'Insert abstract...'
    insert_abstract()
    return redirect(url_for('pubmed.view_pmid_abstract', formula=formula))


@pubmed.route('/formula/<formula>')
def view_pmid_abstract(formula):
    records = get_complete_res_by_formula(formula)
    return render_template('pmid_abstract.html', records=records, formula=formula)


@pubmed.route('/extract_snps', methods=['POST'])
def snps_extraction():
    formula = request.form.get('formula')
    print 'Start extracting snps...'
    extract_snps(formula)
    return redirect(url_for('pubmed.view_pmid_abstract', formula=formula))


@pubmed.route('/download_snps', methods=['POST'])
def download_snps():
    formula = request.form.get('formula')
    generate_csv_by_formula(formula)
    return send_file(
        'output/mentioned_snps.csv', as_attachment=True,
        attachment_filename='mentioned_snps.csv'
    )
