import os
import urllib2

import bs4


def get_ENST(enst_number):
    cmd = 'wget "http://www.ensembl.org/Homo_sapiens/Export/Output/Transcript?db=core;flank3_display=0;' \
          'flank5_display=0;output=fasta;t=%s;param=cdna;param=coding;param=peptide;param=utr5;param=utr3;' \
          'param=exon;param=intron;genomic=unmasked;_format=Text" -O %s.fa' % (enst_number, enst_number)
    os.system(cmd)
    with open('%s.fa' % enst_number) as fi:
        seq = fi.read()
    os.system('rm %s.fa' % enst_number)
    return seq


def get_uuid(nm_number):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nucleotide&term=%s' % nm_number
    response = urllib2.urlopen(url)
    soup = bs4.BeautifulSoup(response.read(), 'html.parser')
    id_list = [str(s).replace('<id>', '').replace('</id>', '') for s in soup('id')]
    if len(id_list) == 1:
        return id_list[0]
    else:
        return None


def get_NM(nm_number):
    uuid = get_uuid(nm_number)
    if uuid is None:
        return ''
    cmd = 'wget "https://www.ncbi.nlm.nih.gov//sviewer/viewer.cgi?tool=portal&save=file&log$=seqview&db=nuccore&' \
          'report=fasta&sort=&id=%s&from=begin&to=end&maxplex=1" -O %s.fa' % (uuid, nm_number)
    os.system(cmd)
    with open('%s.fa' % nm_number) as fi:
        seq = fi.read()
    os.system('rm %s.fa' % nm_number)
    return seq


def get_transcripts(accession_list):
    seq_list = []
    for accession in accession_list:
        if accession.startswith('ENST'):
            seq_list.append(get_ENST(accession))
        elif accession.startswith('NM'):
            seq_list.append(get_NM(accession))
    return '\n'.join(seq_list)


if __name__ == '__main__':
    print get_uuid('NM_002944')
