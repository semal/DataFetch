import urllib2
import bs4


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
    retmax = 1000
    size = 1000
    while size == retmax:
        joined_url = '%s&retstart=%d&retmax=%d' % (url, retstart, retmax)
        response = urllib2.urlopen(joined_url)
        soup = bs4.BeautifulSoup(response.read(), 'html.parser')
        id_list = [str(s).replace('<id>', '').replace('</id>', '') for s in soup('id')]
        size = len(id_list)
        pmid_list.extend(id_list)
        retstart += 1000
    return pmid_list


def test_search_pubmed():
    pmid_list = search_pubmed('?term=breast+cancer+china+chinese+human+mutation')
    assert len(pmid_list) == 126


if __name__ == '__main__':
    test_search_pubmed()
