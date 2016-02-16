import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# for algorithm
from elasticsearch import Elasticsearch
from Algorithm import get_corresponding_algo, get_all_mentioned_algo

# for rosettacode impl
from cassandra.cluster import Cluster
from Implementation import get_all_impls

# for training set labels
import redis

# using support vector regression: features -> ranking score
from sklearn import svm

# for randomly sampling negative training example
import random

# feature extract
from FeatureExtractor import extract_features

def train():
    CORRESPONDING = 1.0
    NON_CORRESPONDING = 0.0
    clf = svm.LinearSVR()

    # cassandra init
    cluster = Cluster(['127.0.0.1'])  # localhost
    session = cluster.connect()  # default key space
    session.set_keyspace('rosettacode')

    # for task names and labels
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    # for algo names and data
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    tasks = get_all_impls(session, rd)
    # # get all task names in rosettacode
    # task_names = rd.hkeys('rosettacode-label-algoname')
    # # get all algo names in elasticsearch algorithm table
    # query = {
    #     "query": {
    #         "match_all" : {}
    #     }
    # }
    # res = es.search(index='throwtable', doc_type='algorithm', body=query)
    algo_names = get_all_mentioned_algo(rd)

    # debugging
    print '# of task_names:', len(tasks)
    print '# of algo_names:', len(algo_names)

    # feature vector
    feature_vector = list()
    # score vector
    score_vector = list()
    print algo_names

    for task in tasks:
        # now only train on tasks that are algorithms, and have wiki pages
        if not task.rank_trainable():
            continue

        # TODO: not using algorithm's data for now
        # # get algorithm's data from our algo db
        # algo = es.get(index='throwtable', doc_type='algorithm',
        #     id=normalize(algo_name), ignore=404)
        # if not result['found']:
        #     print 'corresponding algo is not in elasticsearch'
        #     continue

        # positive:negative = 1:1
        # positive training example
        corres_algo = get_corresponding_algo(task.label)
        feature_vector.append(extract_features(task, corres_algo))
        score_vector.append(CORRESPONDING)

        # negative training example
        random_algo_name = None
        while (random_algo_name is None or random_algo_name == task.label):
            random_algo_name = random.choice(algo_names)
        random_algo = get_corresponding_algo(random_algo_name)
        feature_vector.append(extract_features(task, random_algo))
        score_vector.append(NON_CORRESPONDING)

    # train
    clf.fit(feature_vector, score_vector)
    return clf

# samples_features = a list of features, size = # of samples * # of features
# returns a list of
def classify(model, samples_features):
    return predict(samples_features)

# def mock_extractor(title1, title2):
#     features = list()
#     features.append(fuzz.ratio(title1, title2))
#     features.append(fuzz.partial_ratio(title1, title2))
#     features.append(Simhash(title1).distance(Simhash(title2)))
#     return features

def main():
    train()

if __name__ == '__main__':
    main()
