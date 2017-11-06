# coding=utf-8
import multiprocessing
from time import sleep
import requests
import bs4
import sys
from w3lib.html import remove_tags
import json


def get_mesh(phenotype):
    """
    模拟https://www.nlm.nih.gov/mesh/2016/mesh_browser/MBrowser.html页面的表单提交，获取数据。
    """
    try:
        if phenotype.startswith('https://'):
            r = requests.get(phenotype)
        else:
            url = 'https://www.nlm.nih.gov/cgi/mesh/2016/MB_cgi'
            exact_submit = {
                'term': '%s' % phenotype,
                'exact': 'Find Exact Term'
            }
            # session = requests.session()
            r = requests.post(url, data=exact_submit)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        tags = soup.find_all("tr")
        mesh_heading = ''
        tree_numbers = []
        notes = []
        unique_id = ''
        heading_mapped_to = {}
        for tag in tags:
            th = remove_tags(str(tag.find('th')))
            td = remove_tags(str(tag.find('td')))
            if th.strip() == 'MeSH Heading' or th.strip() == 'Name of Substance':
                mesh_heading = td
            elif th.strip() == 'Tree Number':
                tree_numbers.append(td)
            elif 'Note' in th:
                notes.append(td)
            elif th.strip() == 'Heading Mapped to':
                # heading_mapped_to[td.strip()] = get_mesh(td.strip().replace('*', ''))
                heading_mapped_to[td.strip()] = get_mesh(
                    'https://www.nlm.nih.gov%s' % tag.find('a')['href']
                )
            elif th.strip() == 'Unique ID':
                unique_id = td
        record = {
            'phenotype': phenotype,
            'mesh_heading': mesh_heading,
            'tree_numbers': tree_numbers,
            'note': ';'.join(notes),
            'unique_id': unique_id,
            'heading_mapped_to': heading_mapped_to
        }
        return record
    except:
        sleep(10)
        return {
            'phenotype': phenotype,
            'mesh_heading': 'error',
            'tree_numbers': 'error',
            'note': 'error',
            'unique_id': 'error',
            'heading_mapped_to': 'error',
        }


def read_search_phenotypes(fp):
    phenotypes = []
    with open(fp) as fi:
        for line in fi:
            if line.strip() == '':
                continue
            phenotypes.append(line.strip())
    return phenotypes


def batch(fp):
    phenotypes = read_search_phenotypes(fp)
    pool = multiprocessing.Pool(100)
    result = pool.map(get_mesh, phenotypes)
    json.dump(result, open('output/mesh_code_result.json', 'w'))


if __name__ == '__main__':
    batch(sys.argv[1])
