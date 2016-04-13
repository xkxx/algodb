from elasticsearch import Elasticsearch
from cassandra.cluster import Cluster
import redis

class DB_beans:
    def __init__(self):
        self.cs_rs_ = None
        self.cs_cw_ = None
        self.es_ = None
        self.rd_ = None
        self.feature_cache_ = None
        self.cs_rs_impl_ = None

    def create_cs(self, keyspace):
        cluster = Cluster(['127.0.0.1'])  # localhost
        session = cluster.connect()  # default key space
        session.set_keyspace(keyspace)
        return session

    @property
    def cs_rs(self):
        if self.cs_rs_ is None:
            self.cs_rs_ = self.create_cs('rosettacode')
        return self.cs_rs_

    @property
    def cs_cw(self):
        if self.cs_cw_ is None:
            self.cs_cw_ = self.create_cs('crosswikis')
        return self.cs_cw_

    @property
    def cs_rs_impl(self):
        if self.cs_rs_impl_ is None:
            self.cs_rs_impl_ = self.create_cs('rosettacode_impl')
        return self.cs_rs_impl_

    # rd
    def create_rd(self):
        self.rd_ = redis.StrictRedis(host='localhost', port=6379, db=0)

    @property
    def rd(self):
        if self.rd_ is None:
            self.create_rd()
        return self.rd_

    @property
    def feature_cache(self):
        if self.feature_cache_ is None:
            self.create_feature_cache()
        return self.feature_cache_

    # cache
    def create_feature_cache(self):
        self.feature_cache_ = redis.StrictRedis(host='localhost', port=6379, db=1)

    # es
    def create_es(self):
        self.es_ = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    @property
    def es(self):
        if self.es_ is None:
            self.create_es()
        return self.es_
