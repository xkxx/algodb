from elasticsearch import Elasticsearch
import redis

# get all languages existed in elasticsearch
# output to a file
def get_rosetta_impl_languages(filename='impl_lang.txt'):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    body = {'query': {'match_all': {}}}
    result = es.search(index='throwtable', doc_type='implementation',
        body=body, size=15000)

    languages = set(impl['_source']['language'].encode('utf8')
        for impl in result['hits']['hits'])
    languages = list(languages)
    languages = sorted(languages)

    output = open(filename, 'w+')
    for lang in languages:
        output.write('%s\n' % lang)

# add all language mapping to redis
def add_lang_mapping_from_file(filename):
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    try:
        mapping_file = open(filename)
    except Exception:
        print 'I/O exception'
        return
    for line in mapping_file:
        tokens = line.split('\t')
        if len(tokens) > 1:
            for alternative in tokens[1:]:
                index_language_mapping(rd, alternative, tokens[0])

# index one language mapping to redis
def index_language_mapping(rd, alternative, lang):
    rd.hset('rosetta-language-mapping', alternative, lang)

# reindex existing implementations in elasticsearch to deduplicate
def reindex_language():
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    body = {'query': {'match_all': {}}}
    result = es.search(index='throwtable', doc_type='implementation',
        body=body, size=15000)

    for impl in result['hits']['hits']:
        language = impl['_source']['language']
        if rd.hexists('rosetta-language-mapping', language):
            print impl['_id']
            language = rd.hget('rosetta-language-mapping', language)
            es.index(index='throwtable', doc_type='implementation',
                id=replace_lang_from_id(impl['_id'], language.decode('utf8')),
                body=impl['_source'])
            es.delete(index='throwtable', doc_type='implementation',
                id=impl['_id'])

def replace_lang_from_id(id, replacement):
    return ':'.join(id.split(':')[0:2] + [replacement])

if __name__ == '__main__':
    # add_lang_mapping_from_file('impl_lang.txt')
    reindex_language()
