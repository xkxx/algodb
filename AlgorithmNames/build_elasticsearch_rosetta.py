from elasticsearch import Elasticsearch

from parseRosetta import Task
from parseRosetta import site

from build_elasticsearch_wikipedia import INDEX_NAME
from build_elasticsearch_wikipedia import normalize

import redis

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
rd = redis.StrictRedis(host='localhost', port=6379, db=0)

def index_rosetta():
    category = site.Pages['Category:Programming Tasks']
    for page in category:
        print 'looking for page:', page.page_title
        algo_id = get_corres_wikipedia_algo_id(page)
        if algo_id is not None:
            index_rosetta_page(page, algo_id)

def index_rosetta_page(page, algo_id):
    pagetask = Task(page)  # extract data from page using Task from pr

    for impl in pagetask.solutions:
        body = {
            'language': impl['language'],
            'algorithm': [algo_id],
            'source': 'rosetta',
            'implementation': impl['content']
        }

        print '----task name:', pagetask.task_name
        print '----lang:', impl['language']

        es.index(index=INDEX_NAME, doc_type='implementation',
            id='rosetta:' + normalize(pagetask.task_name) + ':' +
            impl['language'].decode('utf8'), body=body)

# for each of the wiki links in rosetta code algorithm page,
# check if we've indexed this algorithm,
# return the id of the corresponding algorithm, None if not found
def get_corres_wikipedia_algo_id(page):
    links = page.iwlinks()
    haswikilink = False
    for (linksite, linktitle) in links:
        if linksite == 'wp':
            haswikilink = True
            print '--looking for linktitle:', linktitle
            id = convert_to_id(linktitle)
            print '--looking for id:', id
            result = es.get(index=INDEX_NAME, doc_type='algorithm',
                id=id, ignore=404)
            if result['found']:
                rd.sadd('rosetta-mapping-success', page.page_title)
                return id
    print '--no corresponding algo in wiki'
    if haswikilink:
        # the page has a wiki link,
        # but the algorithm of that link is not indexed
        rd.sadd('rosetta-mapping-error-link-not-indexed', page.page_title)
    else:
        rd.sadd('rosetta-mapping-error', page.page_title)
    return None

def convert_to_id(title):
    return str(title.encode('utf8').lower()).replace('_', '-')

if __name__ == '__main__':
    index_rosetta()
