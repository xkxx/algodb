from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from unicodedata import normalize

def index_top_results(doc, es):
    query = {'query': { 'multi_match': {
        "query": doc['name'],
        "type": "phrase",
        "fields": ["description", "plaintext-readme"]
    }}}
    res = es.search(index='throwtable', doc_type='algorithm', body=query, size=10)
    hits = res['hits']['hits']
    for hit in hits:
        print hit["_id"], hit["_score"]
        if hit["_score"] > 2.0:
            id = hit['_id']
            pkg = hit['_source']
            impls = hit.get('algorithm', [])
            impls.append(doc['_id'])
            pkg['algorithm'] = impls
            print "Adding: ", id, impls
            es.index(id=id, index='throwtable', doc_type='implementation', body=pkg)

def scan_algorithm(es):
    body = {'query': {'match_all': {}}}

    result = scan(es, index='throwtable', doc_type='algorithm',
        query=body)

    for hit in result:
        print '======================='
        print hit['_id']
        doc = hit['_source']
        name = doc['name']
        index_top_results(doc, es)

if __name__ == '__main__':
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    scan_algorithm(es)
    print 'done'
