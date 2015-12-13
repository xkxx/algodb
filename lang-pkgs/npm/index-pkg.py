import sys, os
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'NEL'))
from elasticsearch import Elasticsearch
import json
import time
import math
import stringmatching_npm as stringmatch


def get_text_content(pkg):
    return [
        (pkg['desc'], 2.0),
        (pkg['readme'], 1.0)
    ]

def match_valid(algo, score, weight):
    if score > 1.0:
        return True

def get_es_id(pkg):
    return 'npm:%s:js' % pkg['name']

def compute_pkg_weight(pkg):
    return pkg['downloads'] * 1.0 / math.log(int(time.time() * 1000) - pkg['timeUpdated'])

def add_to_db(pkg, impls, es):
    es.index(index='throwtable',
    doc_type='implementation',
    id=get_es_id(pkg),
    body={
        'language': 'js',
        'algorithm': [impls],
        'source': 'npm',
        'description': pkg['desc'],
        'instruction': {
            'package': pkg['name'],
            'command': 'npm install ' + pkg['name'],
            'content': pkg['readme']
        },
        'popularity': compute_pkg_weight(pkg)

    })

def get_links(pkg, es):
    texts = get_text_content(pkg)
    impls = []
    for (text, weight) in texts:
        result = stringmatch.link_algorithm(text, es)
        print result
        for (algo, score) in result:
            if match_valid(algo, score, weight):
                impls.append(algo)
    return impls

def index_package(line):
    pkg = json.loads(line)
    impls = get_links(pkg, es)
    if len(impls) > 0:
        add_to_db(pkg, impls, es)

def work():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    dump = open('results.json')
    for line in dump:
        index_package(line, es)

def test_query(desp):
    from pprint import pprint
    pprint(stringmatch.link_algorithm(desp, es), width=1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        work()
    else:
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        from subprocess import check_output
        from pprint import pprint
        line = check_output(["node", "get-desc.js", sys.argv[1]])
        print line
        pkg = json.loads(line)
        impls = get_links(pkg, es)
        pprint(impls, width=1)
