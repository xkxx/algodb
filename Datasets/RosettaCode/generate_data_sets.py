import sys
reload(sys)
sys.setdefaultencoding('utf8')

import mwclient as mw
from cassandra.cluster import Cluster



def store_rosettacode_cassandra():
    site = mw.Site('rosettacode.org', path='/mw/')
    cluster = Cluster(['127.0.0.1'])  # localhost
    session = cluster.connect()  # default key space
    session.set_keyspace('rosettacode')

    for page in site.Pages['Category:Programming Tasks']:
        session.execute("INSERT INTO queries (anchor, cprob, entity) VALUES (%s, %s, %s)", [anchor.encode('utf8').decode('utf8'), num(cprob), entity.encode('utf8').decode('utf8')])

# TODO
def store_label_redis():
    pass
