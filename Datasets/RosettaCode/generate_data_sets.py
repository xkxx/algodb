import sys
reload(sys)
sys.setdefaultencoding('utf8')

import mwclient as mw
from cassandra.cluster import Cluster
import random

import redis

def store_rosettacode_cassandra():
    site = mw.Site('rosettacode.org', path='/mw/')
    cluster = Cluster(['127.0.0.1'])  # localhost
    session = cluster.connect()  # default key space
    session.set_keyspace('rosettacode')

    for page in site.Pages['Category:Programming Tasks']:
        print page.page_title
        iwlinks = set([el[1] for el in page.iwlinks()])
        categories = set([el.page_title for el in page.categories()])
        session.execute("INSERT INTO rosettacode (page_title, categories, iwlinks, text) VALUES (%s, %s, %s, %s)", [page.page_title, categories, iwlinks, page.text()])


def store_label_redis():
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    labelfile = list(open('labelfile.txt'))
    random.shuffle(labelfile)
    devset = labelfile[:-150]
    testset = labelfile[-150:]
    for line in devset:
        (task_name, algo_name, is_algo) = line.strip().split('\t')
        if is_algo == 'y':
            rd.sadd('rosettacode-label-isalgo', task_name)
        if len(algo_name) > 0:
            rd.hset('rosettacode-label-algoname', task_name, algo_name)

    for line in testset:
        (task_name, algo_name, is_algo) = line.strip().split('\t')
        if is_algo == 'y':
            rd.sadd('rosettacode-test-label-isalgo', task_name)
        if len(algo_name) > 0:
            rd.hset('rosettacode-test-label-algoname', task_name, algo_name)

def main():
    store_rosettacode_cassandra()
    # store_label_redis()

if __name__ == '__main__':
    main()
