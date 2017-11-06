import os
import multiprocessing


def run(gene):
    fn_list = os.listdir('result')
    if '%s.tsv' % gene not in fn_list:
        os.system(
            'aria2c --header="Cookie:donation-popup=true; '
            'sessionid=o5tznyomgtr5x70wmej8hlyg4sck0k8z; _ga=GA1.2.801700580.1476441682" '
            '"https://omim.org/search/?index=geneMap&search=%s&start=1&limit=10000&format=tab" '
            '-o result/%s.tsv' % (gene, gene)
        )


def get_genes():
    genes = []
    with open('/home/jjiang/omim.txt') as fi:
        for line in fi:
            genes.append(line.strip())
    return genes


def multi_run():
    genes = get_genes()
    pool = multiprocessing.Pool(100)
    pool.map(run, genes)


def get_all_records():
    genes = get_genes()
    for gene in genes:
        with open('result/%s.tsv' % gene) as fi:
            for line in fi:
                if line.startswith('Gene Map Search'):
                    continue
                try:
                    if gene in line.split('\t')[2]:
                        yield line
                except IndexError:
                    continue


def generate_all():
    with open('all_record.tsv', 'w') as fo:
        for line in get_all_records():
            fo.write(line)


if __name__ == '__main__':
    generate_all()
