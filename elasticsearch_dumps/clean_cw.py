from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from unicodedata import normalize

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

body = {'query': {'match_all': {}}}

result = scan(es, index='throwtable', doc_type='algorithm',
        query=body)

for hit in result:
  print hit['_id']
  doc = hit['_source']
  altnames = doc.get('alt_names', [])
  altnames = [
    altname for altname in altnames
    if 'wiki' not in altname.lower()
  ]
  doc['alt_names'] = altnames
  es.index(id=hit['_id'], index='throwtable', doc_type='algorithm', body=doc)

print 'done'
