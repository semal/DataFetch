import csv
import json
import multiprocessing
import os
import sqlite3
import sys
import urllib2
import bs4

reload(sys)
sys.setdefaultencoding('utf8')


def connect_db():
    conn = sqlite3.connect('db.sqlite')
    return conn


def get_unique_snps():
    cursor = connect_db().execute('SELECT * FROM complete_res')
    snps = []
    for row in cursor:
        sub_snps = row[1].split(',')
        snps.extend(sub_snps)
    snps = list(set(snps))

    with open('unique_snps.txt', 'w') as fo:
        for snp in snps:
            if snp == '':
                continue
            fo.write(snp.strip() + '\n')


def get_formulas_in_db():
    conn = connect_db()
    cursor = conn.execute('SELECT formula FROM formulas')
    formulas = []
    for row in cursor:
        formulas.append(row[0])
    return formulas


def get_formula_id(formula):
    conn = connect_db()
    cursor = conn.execute(
        'SELECT formula_id FROM formulas WHERE formula = "%s"' % formula.replace('"', '""')
    )
    formula_id = None
    for row in cursor:
        formula_id = row[0]
    return formula_id


def get_complete_res_by_formula(formula):
    conn = connect_db()
    pmid_list = search_pubmed(formula)
    print len(pmid_list), 'Got it!'
    cursor = conn.execute(
        'SELECT pmid, mutations, title, abstract FROM complete_res '
        'WHERE pmid IN (%s)' % ','.join(["'%s'" % pmid for pmid in pmid_list])
    )
    records = []
    for row in cursor:
        snps = ', '.join(list(set([snp.strip() for snp in row[1].split(',')])))
        records.append([row[0], snps, row[2], row[3]])
    return records


def get_pmid_list_in_db(table='pubmed_papers'):
    conn = connect_db()
    cursor = conn.execute('SELECT pmid FROM %s' % table)
    pmid_list = []
    for row in cursor:
        pmid_list.append(row[0])
    return pmid_list


def scrapy_pmid_abstract(pmid_list):
    print 'Start get pmid in db...'
    pmid_in_db = get_pmid_list_in_db()
    print 'Got', len(pmid_in_db), 'in database.', 'Start remove db including pmids...'
    # pmids = ','.join([pmid for pmid in pmid_list if pmid not in pmid_in_db])
    pmid_list = list(set(pmid_list).difference(set(pmid_in_db)))
    pmids = ','.join(pmid_list)
    print 'Left', len(pmids.split(',')), 'Scrapy them!'
    if pmids == '':
        return 'Exist!'
    os.system('rm pubmed_abstract.json')
    os.system(
        'venv/bin/scrapy crawl fetch_pubmed_abstract -a pmids="%s" '
        '-o pubmed_abstract.json -t json' % pmids
    )
    with open('pubmed_abstract.json') as fi:
        res = fi.read()
    if res.strip() == '':
        return 'Got nothing!'
    else:
        return 'Got something!'


def insert_formula(formula):
    os.system(
        '(echo insert into formulas \\(formula\\) values \\(\\"%s\\"\\)\\;) '
        '| sqlite3 db.sqlite' % formula
    )


def insert_abstract():
    conn = connect_db()
    with open('pubmed_abstract.json') as fi:
        res = json.load(fi)
    for rec in res:
        if 'pmid' in rec.keys():
            pmid = rec['pmid'].strip()
            title = rec['title'].strip().replace('"', '""')
            abstract = rec['abstract'].replace('"', '""') if 'abstract' in rec.keys() else ''
            abstract = abstract.strip() if abstract is not None else ''
            conn.execute(
                'insert into pubmed_papers (pmid, title, abstract) '
                'VALUES ("%s", "%s", "%s")' % (pmid, title, abstract)
            )
    conn.commit()
    conn.close()


def get_abstract_in_db(pmid_list):
    conn = connect_db()
    cursor = conn.execute('SELECT pmid, abstract FROM pubmed_papers')
    abstract_list = []
    new_pmid_list = []
    for row in cursor:
        if row[0] in pmid_list:
            new_pmid_list.append(row[0])
            abstract_list.append(row[1])
    return new_pmid_list, abstract_list


def extract_snps_sub(args):
    file_names = os.listdir('result')
    if '%s.seth' % args[1] not in file_names:
        os.system(
            'java -cp seth-1.3-jar-with-dependencies.jar '
            'seth.ner.wrapper.SETHNERAppMut "%s" >result/%s.seth' % (args[0], args[1])
        )


def clean_seth_files(pmid_list):
    pmid_fn_list = ['%s.seth' % pi for pi in pmid_list]
    fo = csv.writer(open('mentioned_snps.csv', 'w'))
    for fn in os.listdir('result'):
        if not fn.endswith('.seth'):
            continue
        if fn not in pmid_fn_list:
            continue
        snps = []
        with open('result/%s' % fn) as fi:
            for line in fi:
                if line.startswith('MutationMention'):
                    snps.append(line.split(',')[4].split('=')[1])
            fo.writerow(
                [fn.split('.')[0], ','.join(snps)]
            )


def extract_snps(formula):
    pmid_list = search_pubmed(formula)
    pmid_list_in_db = get_pmid_list_in_db('mentioned_snps')
    pmid_list = [pmid for pmid in pmid_list if pmid not in pmid_list_in_db]
    pmid_list, abstract_list = get_abstract_in_db(pmid_list)
    os.chdir('lib/seth')
    pool = multiprocessing.Pool(40)
    queue = []
    for abstract, pmid in zip(abstract_list, pmid_list):
        queue.append((abstract, pmid))
    pool.map(extract_snps_sub, queue)
    clean_seth_files(pmid_list)
    os.chdir('../..')
    conn = connect_db()
    with open('lib/seth/mentioned_snps.csv') as fi:
        reader = csv.reader(fi)
        for row in reader:
            pmid, mutations = row[0], row[1]
            conn.execute(
                'REPLACE INTO mentioned_snps (pmid, mutations) '
                'VALUES ("%s", "%s")' % (pmid, mutations)
            )
    conn.commit()
    conn.close()


def get_formulas():
    conn = connect_db()
    formulas = []
    cursor = conn.execute('SELECT formula FROM formulas;')
    for row in cursor:
        formulas.append(row[0])
    return formulas


def search_pubmed(search_formula):
    """
    Using search_formula to search papers though pubmed e-search api.

    Parameters
    -----------
    search_formula : str
        search term, like "?term=breast+cancer+china+chinese+human+mutation"

    Returns
    --------
    pmid_list : list
        list of pmid
    """
    pmid_list = []
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    url = '/'.join([base_url, search_formula])
    retstart = 0
    retmax = 100000
    size = retmax
    while size == retmax:
        joined_url = '%s&retstart=%d&retmax=%d' % (url, retstart, retmax)
        response = urllib2.urlopen(joined_url)
        soup = bs4.BeautifulSoup(response.read(), 'html.parser')
        id_list = [str(s).replace('<id>', '').replace('</id>', '') for s in soup('id')]
        size = len(id_list)
        pmid_list.extend(id_list)
        retstart += retmax
    return pmid_list


def generate_csv_by_formula(formula):
    pmid_list = search_pubmed(formula)
    os.system(
        'sqlite3 -header -csv db.sqlite "select pmid, mutations '
        'from complete_res where pmid IN (%s);" '
        '>mentioned_snps.csv' % ','.join(["'%s'" % pmid for pmid in pmid_list])
    )


if __name__ == '__main__':
    search_pubmed(
        '?term=%28chinese%5BTitle%2FAbstract%5D+OR+CHN%5BTitle%2FAbstract%5D+OR+Korea*%5BTitle%2FAbstract%5D+OR+Japan*%5BTitle%2FAbstract%5D+OR+China%5BTitle%2FAbstract%5D+OR+Taiwan*%5BTitle%2FAbstract%5D+OR+Singapore*%5BTitle%2FAbstract%5D+OR+Asian*%5BTitle%2FAbstract%5D%29+AND+%28single+nucleotide+polymorphism*%5BTitle%2FAbstract%5D+OR+SNP*%5BTitle%2FAbstract%5D+OR+variant*%5BTitle%2FAbstract%5D+OR+polymorphism*%5BTitle%2FAbstract%5D%29+AND+%28association*%5BTitle%2FAbstract%5D+OR+gwas%5BTitle%2FAbstract%5D+OR+genome+wide+association*%5BTitle%2FAbstract%5D+OR+genome-wide+association*%5BTitle%2FAbstract%5D+OR+genome-wide+meta-analysis*%5BTitle%2FAbstract%5D+OR+meta+analysis*%5BTitle%2FAbstract%5D+OR+meta-analysis*%5BTitle%2FAbstract%5D+OR+replication*%5BTitle%2FAbstract%5D%29+AND+%22humans%22%5BMeSH+Terms%5D'
    )
