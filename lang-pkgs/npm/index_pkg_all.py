import sys, os
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'NEL'))
from elasticsearch import Elasticsearch
import json
import time
import math
import stringmatching_npm as stringmatch
from dateutil import parser as dateparser
from datetime import datetime
from collections import Counter
from RAKE import Rake
import requests
from markdown_extract import extractText

def match_valid(algo, score):
    if score > 5.0:
        return True

def get_es_id(pkg):
    return 'npm:%s:js' % pkg['name']

def compute_pkg_weight(pkg):
    ctime = pkg.get('timeUpdated', None)
    if ctime is None:
      return 0
    return pkg.get('downloads', 0) * 1.0 / math.log(
        (datetime.utcnow() -
            dateparser.parse(ctime, ignoretz=True)).days)

def add_to_db(pkg, es):
    keywords = pkg.get('keywords', [])
    readme = pkg.get('readme', '')
    if type(readme) != str and type(readme) != unicode:
        # print 'No Readme Found'
        readme = ''
    plaintextRM = extractText(readme)

    es.index(index='throwtable',
    doc_type='implementation',
    id=get_es_id(pkg),
    body={
        'language': 'JavaScript',
        'algorithm': [],
        'source': 'npm',
        'description': pkg.get('desc', ''),
        'plaintext-readme': plaintextRM,
        'instruction': {
            'package': pkg['name'],
            'command': 'npm install ' + pkg['name'],
            'content': readme
        },
        'popularity': compute_pkg_weight(pkg)
    })

def index_package(line, es):
    pkg = json.loads(line)
    add_to_db(pkg, es)

def get_npm_pkg(pkgName):
    res = requests.get('http://localhost:5984/npm/%s' % pkgName)
    return res.json()

def work():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    dump = open('results.json')
    ctr = 0
    for line in dump:
        ctr += 1
        print ctr
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
        pkg = json.loads(line)
        impls = get_links(pkg, es)
        pprint(impls, width=1)
