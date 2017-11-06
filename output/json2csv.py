# coding=utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import json
import csv


def json2csv():
    with open('pubmed_abstract.json') as fi:
        res = json.load(fi)

    fo = csv.writer(open('pubmed_abstract.csv', 'w'))
    # fo.writerow(['id', 'pmid', 'title', 'abstract'])

    for rec in res:
        id = rec['id'].strip()
        pmid = rec['pmid'].strip()
        title = rec['title'].strip()
        abstract = rec['abstract']
        fo.writerow(
            [
                id,
                pmid,
                title,
                abstract.strip() if abstract is not None else '',
            ]
        )
