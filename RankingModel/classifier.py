# for utf8 encoding and decoding
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# # for task data
# from cassandra.cluster import Cluster

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

# ranking
from collections import Counter

# feature extract
from FeatureExtractor import extract_features

# return [(impl, corres_algo)]
def get_trainable_data(cas, rd):
    tasks = get_all_impls(cas, rd)
    results = []

    for task in tasks:
        # now only train on tasks that are algorithms, and have wiki pages
        if not task.rank_trainable():
            continue
        corres_algo = get_corresponding_algo(task.label)
        results.append((task, corres_algo))

def split_data(data):
    train = data[:-100]
    valid = data[-100:]
    return (train, valid)

# return feature_vector, score_vector
def create_training_vectors(data, rd):
    # feature vector
    feature_vector = list()
    # score vector
    score_vector = list()
    algo_names = get_all_mentioned_algo(rd)

    CORRESPONDING = 1.0
    NON_CORRESPONDING = 0.0

    # positive:negative = 1:1

    for (task, corres_algo) in data:
        # positive training example
        feature_vector.append(extract_features(task, corres_algo))
        score_vector.append(CORRESPONDING)
        # negative training example
        random_algo = None
        while (random_algo is None or random_algo == task.label):
            random_algo = random.choice(algo_names)
        feature_vector.append(extract_features(task, random_algo))
        score_vector.append(NON_CORRESPONDING)

    return (feature_vector, score_vector)

def train(data, rd):
    (feature_vector, score_vector) = create_training_vectors(data, rd)
    clf = svm.LinearSVR()

    # train
    clf.fit(feature_vector, score_vector)
    return clf

# samples_features = a list of features, size = # of samples * # of features
# returns a list of
def classify(model, sample, candidates):
    ranks = Counter()
    for cand in candidates:
        sample_features = extract_features(sample, cand)
        [result] = model.predict([sample_features])
        ranks[cand] = result
    return (ranks.most_common())

def validation(model, samples):
    all_algos = get_all_mentioned_algo()
    recranks = []
    for (impl, corres_algo) in samples:
        result = classify(model, impl, all_algos)
        keys = zip(*result)
        print "Impl:", impl
        print "Algo:", corres_algo
        print "Top Rank:", result[0:3]
        rank = keys.index(corres_algo)
        print "Rank of Correct Algo:", rank
        recranks.append(1.0 / rank)
    print
    print "Avg Rank Reciprocal:", sum(recranks) / 1.0 / len(recranks)

def main():
    # cassandra init
    cluster = Cluster(['127.0.0.1'])  # localhost
    session = cluster.connect()  # default key space
    session.set_keyspace('rosettacode')

    # for task names and labels
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    # for algo names and data
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    all_trainable = get_trainable_data(session, rd)
    (train, valid) = split_data(all_trainable)

    print "Training..."
    model = train(train, rd)

    print "Verifying..."

    validation(model, valid)


if __name__ == '__main__':
    main()
