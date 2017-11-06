import json
import csv
import sys

reload(sys)
sys.setdefaultencoding('utf8')


def get_tree_numbers(rec):
    tree_nums = []
    if rec['tree_numbers'] != 'error' and len(rec['tree_numbers']) > 0:
        return rec['tree_numbers']
    elif rec['heading_mapped_to'] != 'error' and len(rec['heading_mapped_to'].keys()) > 0:
        for k, v in rec['heading_mapped_to'].items():
            tree_nums.extend(get_tree_numbers(v))
        return tree_nums
    else:
        return tree_nums


def process():
    with open('output/mesh_code_result.json') as fi:
        result = json.load(fi)

    tree_number_max_count = max([len(get_tree_numbers(record)) for record in result])

    with open('output/mesh_code_result.csv', 'w') as fo:
        writer = csv.writer(fo)
        header_row = ['Phenotype', 'MeSH Heading/Name of Substance']
        header_row.extend(['Tree Number'] * tree_number_max_count)
        header_row.append('Notes')
        header_row.append('Heading Mapped to')
        writer.writerow(header_row)
        for record in result:
            row = [record['phenotype'].strip(), record['mesh_heading'].strip()]
            tree_numbers = get_tree_numbers(record)
            empty = [''] * (tree_number_max_count - len(tree_numbers))
            for tn in tree_numbers:
                row.append(tn.strip())
            for e in empty:
                row.append(e)
            row.append(record['note'].strip())
            row.append(
                ';'.join(record['heading_mapped_to'].keys())
                if record['heading_mapped_to'] != 'error' else 'error'
            )
            writer.writerow(row)
