# for utf8 encoding and decoding
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# # for task data
# from cassandra.cluster import Cluster

# for algorithm
from Algorithm import get_corresponding_algo, get_all_mentioned_algo

# for rosettacode impl
from Implementation import get_all_tasks

# using support vector regression: features -> ranking score
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier

# for randomly sampling negative training example
import random

# ranking
from collections import Counter

# feature extract
from FeatureExtractor import extract_features

from db_dependency import DB_beans

from itertools import chain, combinations

# return [(impl, corres_algo)]
def get_trainable_data(db):
    tasks = get_all_tasks(db)
    # results = []

    return tasks
    # for task in tasks:
    #     now only train on tasks that are algorithms, and have wiki pages
    #     if not task.rank_trainable():
    #         continue
    #     results.append(task)

def split_data(data):
    k = 5
    per_split = (len(data) + k - 1) / k

    splits = list()
    for i in range(5):
        cur_start = i * per_split
        left = len(data) - cur_start
        splits.append(data[cur_start:(cur_start + min(per_split, left))])
    return splits

# return feature_vector, score_vector
def create_training_vectors(data, db, num_neg=1):
    # feature vector
    feature_vector = list()
    # score vector
    score_vector = list()
    algo_names = get_all_mentioned_algo(db)

    CORRESPONDING = 1.0
    NON_CORRESPONDING = 0.0

    # positive:negative = 1:1

    for task in data:
        if task.label is not None and task.is_algo:
            # positive training example
            feature_vector.append(extract_features(task, task.label))
            score_vector.append(CORRESPONDING)

        # negative training example
        for i in range(num_neg):
            random_algo = None
            while (random_algo is None or random_algo == task.label):
                random_algo = random.choice(algo_names)
            feature_vector.append(extract_features(task, random_algo))
            score_vector.append(NON_CORRESPONDING)

    return (feature_vector, score_vector)

def train_ranking(feature_vector, score_vector):
    clf = svm.LinearSVR()
    # train
    clf.fit(feature_vector, score_vector)

    return clf

def train_threshold(feature_vector, score_vector, ranking):
    # all_algos = get_all_mentioned_algo(db)
    # feature vector
    stump_features = list()
    # score vector
    stump_scores = list()
    # first try rank training set on trained model
    predictions = ranking.predict(feature_vector)
    # then train decision stump
    stump_features = predictions
    stump_scores = [1 if score == 1 else -1 for score in score_vector]

    clf = DecisionTreeClassifier()
    clf.fit(stump_features, stump_scores)
    return clf

def train(data, db):
    (feature_vector, score_vector) = create_training_vectors(data, db)
    # first train ranking model
    ranking = train_ranking(feature_vector, score_vector)
    threshold = train_threshold(data, ranking)

    return (ranking, threshold)

# samples_features = a list of features, size = # of samples * # of features
# returns a list of
def rank(model, sample, candidates):
    ranks = Counter()
    for cand in candidates:
        sample_features = extract_features(sample, cand)
        [result] = model.predict([sample_features])
        ranks[cand] = result
    return ranks.most_common()

def classify(model, sample, candidates):
    (ranking, threshold) = model
    results = classify(ranking, sample, candidates)
    (topcand, toprank) = results[0]
    guess = None
    if threshold.predict([toprank]) == 1:
        guess = topcand

    return (guess, results)

def validation(model, samples, db):
    all_algos = get_all_mentioned_algo(db)
    recranks = []
    corrects = 0
    for impl in samples:
        (guess, result) = classify(model, impl, all_algos)
        keys = zip(*result)[0]
        print "Impl:", impl
        print "Algo:", impl.label
        print "Prediction:", guess
        print "Top Rank:", result[0:3]
        rank = keys.index(impl.label) + 1
        print "Rank of Correct Algo:", rank
        recranks.append(1.0 / rank)
        if guess == impl.label:
            corrects += 1
    meanrank = sum(recranks) * 1.0 / len(samples)
    accuracy = corrects * 1.0 / len(samples)

    print
    print "Avg Rank Reciprocal:", meanrank
    print "Total correct:", corrects
    return (meanrank, accuracy)

def main():
    db = DB_beans()

    all_trainable = get_trainable_data(db)
    print all_trainable
    splits = split_data(all_trainable)

    trains = list(combinations(splits, 4))
    coefs = []
    meanranks = []
    corrects = []

    for i in range(5):
        train_data = list(chain(*trains[i]))
        valid_data = splits[4 - i]

        print "Training Set:", len(train_data)
        print "Validation Set:", len(valid_data)

        print "Training..."
        model = train(train_data, db)

        print "Feature weights:", model[0].coef_

        print "Verifying..."

        (m, c) = validation(model, valid_data, db)
        coefs.append(model.coef_)
        meanranks.append(m)
        corrects.append(c)

    print "Coefs: ", coefs
    print "Mean MRR: ", sum(meanranks) / 5.0
    print "Mean corrects: ", sum(corrects) / 5.0

if __name__ == '__main__':
    main()
