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

rk = Rake('SmartStoplist.txt')

def get_text_content(pkg):
    desc = pkg.get('desc', '')
    keywords = pkg.get('keywords', [])
    readme = pkg.get('readme', '') or ''
    if type(readme) != str and type(readme) != unicode:
        # print 'No Readme Found'
        readme = ''
    readmeText = extractText(readme)
    # print 'readme', readmeText
    parsedKeywords = rk.run(readmeText)
    # print 'rake', parsedKeywords
    results = []
    for kw in keywords:
        if len(kw) > 2:
            results.append((kw, 2.0))
    for (kw, score) in parsedKeywords:
        if score > 3:
          results.append((kw, 1.2 * math.log(score, 4)))
    if len(desc) > 2:
        results.append((desc, 1.0))
    return results

def match_valid(algo, score):
    if score > 5.0:
        return True

def get_es_id(pkg):
    return 'npm:%s:js' % pkg['name']

def compute_pkg_weight(pkg):
    return pkg.get('downloads', 0) * 1.0 / math.log(
        (datetime.utcnow() -
            dateparser.parse(pkg['timeUpdated'], ignoretz=True)).days)

def add_to_db(pkg, impls, es):
    es.index(index='throwtable',
    doc_type='implementation',
    id=get_es_id(pkg),
    body={
        'language': 'JavaScript',
        'algorithm': impls,
        'source': 'npm',
        'description': pkg.get('desc', ''),
        'instruction': {
            'package': pkg['name'],
            'command': 'npm install ' + pkg['name'],
            'content': pkg.get('readme', '')
        },
        'popularity': compute_pkg_weight(pkg)

    })

def get_links(pkg, es):
    texts = get_text_content(pkg)
    # print texts
    cands = Counter()
    for (text, weight) in texts:
        # print "Weight:", weight
        # print "Text:", text, '\n'
        result = stringmatch.link_algorithm(text, es)
        # print result
        for (algo, score) in result:
            cands[algo] += score * weight

    impls = []
    for (algo, score) in cands.most_common():
        # print algo, score
        if match_valid(algo, score):
            impls.append(algo)
    return impls

def index_package(line, es):
    pkg = json.loads(line)
    impls = get_links(pkg, es)
    if len(impls) > 0:
        add_to_db(pkg, impls[:1], es)

def get_npm_pkg(pkgName):
    res = requests.get('http://localhost:5984/npm/%s' % pkgName)
    return res.json()

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
        pkg = json.loads(line)
        impls = get_links(pkg, es)
        pprint(impls, width=1)
