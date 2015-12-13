import mwclient as mw
import redis
import random
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
site = mw.Site('rosettacode.org', path='/mw/')
r = redis.StrictRedis()

def get_sample():
    pages = list(site.Pages['Category:Programming Tasks'])

    sample = random.sample(pages, 100)

    for page in sample:
        r.sadd('samples', page.page_title)

def get_sample_ids():
    body = {'query': {'match_all': {}}}
    result = es.search(index='throwtable', doc_type='implementation',
        body=body, size=15000)

    for impl in result['hits']['hits']:
        print impl['_id']
        task_name = impl['_id'].split(':')[1]
        if r.hexists('rosetta-id-taskname-mapping', task_name):
            continue
        r.hset('rosetta-id-taskname-mapping', task_name, impl['_id'])

if __name__ == '__main__':
    get_sample_ids()
