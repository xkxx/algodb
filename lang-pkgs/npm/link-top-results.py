from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from unicodedata import normalize

ctrl = [0]
def index_top_results(doc, docid, es):
    query = {'query': { 'multi_match': {
        "query": doc['name'],
        "type": "phrase",
        "slop": 1,
        "fields": ["description", "plaintext-readme"]
    }}}
    res = es.search(index='temp', doc_type='implementation', body=query, size=30)
    hits = res['hits']['hits']
    for hit in hits:
        print hit["_id"], hit["_score"]
        print '-------------------'
        pkgid = hit['_id']
        pkg = hit['_source']
        print pkg['plaintext-readme']
        if hit["_score"] > 1.0:
            impls = hit.get('algorithm', [])
            if docid not in impls:
                impls.append(docid)
            pkg['algorithm'] = impls
            print "Adding: ", pkgid, impls
            es.index(id=pkgid, index='throwtable', doc_type='implementation', body=pkg)
            es.index(id=pkgid, index='temp', doc_type='implementation', body=pkg)
        elif hit["_score"] > 0.4:
            ctrl[0] += 1

def scan_algorithm(es):
    body = {'query': {'match_all': {}}}

    result = scan(es, index='throwtable', doc_type='algorithm',
        query=body)

    for hit in result:
        print '======================='
        print hit['_id']
        doc = hit['_source']
        name = doc['name']
        index_top_results(doc, hit['_id'], es)
    print ctrl[0]

if __name__ == '__main__':
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    scan_algorithm(es)
    print 'done'
