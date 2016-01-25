import mwclient as mw
import redis
import random
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

r = redis.StrictRedis()

def get_sample():
    site = mw.Site('rosettacode.org', path='/mw/')
    pages = list(site.Pages['Category:Programming Tasks'])

    sample = random.sample(pages, 100)

    for page in sample:
        r.sadd('samples', page.page_title)

def get_sample_ids():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    body = {'query': {'match_all': {}}}
    result = scan(es, index='throwtable', doc_type='implementation',
        body=body, scroll='5m')

    for impl in result:
        tokens = impl['_id'].split(':')
        if tokens[0] == 'rosetta':
            print impl['_id']
            task_name = impl['_id'].split(':')[1]
            if r.hexists('rosetta-id-taskname-mapping', task_name):
                continue
            r.hset('rosetta-id-taskname-mapping', task_name, impl['_id'])

def get_sample_ids_language_specified(lang):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    body = {'query': {'match_all': {}}}
    result = es.search(index='throwtable', doc_type='implementation',
        body=body, size=15000)

    for impl in result['hits']['hits']:
        tokens = impl['_id'].split(':')
        if tokens[0] == 'rosetta' and tokens[-1] == 'python':
            print impl['_id']
            task_name = impl['_id'].split(':')[1]
            if r.hexists('rosetta-id-taskname-mapping', task_name):
                continue
            r.hset('rosetta-id-taskname-mapping', task_name, impl['_id'])

if __name__ == '__main__':
    if not r.exists('samples'):
        print 'Please create the sample first, by calling get_sample(),'
        print 'or check if you run redis-server in the wrong folder.'
    else:
        if r.exists('rosetta-id-taskname-mapping'):
            r.delete('rosetta-id-taskname-mapping')
        get_sample_ids_language_specified('python')
