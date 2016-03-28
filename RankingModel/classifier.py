# for utf8 encoding and decoding
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# # for task data
# from cassandra.cluster import Cluster

# for algorithm
from Algorithm import get_all_mentioned_algo

# for rosettacode impl
from Implementation import get_all_tasks

# for randomly sampling negative training example
import random

# feature extract
from FeatureExtractor import extract_features

from db_dependency import DB_beans

from itertools import chain, combinations

# models
from RankingClassifier import RankingClassifier

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

def validation(model, samples, eval_results):
    for impl in samples:
        print "Impl:", impl
        print "Algo:", impl.label
        prediction = model.classify(impl)
        guess = prediction[0]
        print "Prediction:", guess
        eval_results['corrects'].append(guess == impl.label)
        # classifier-defined metrics
        model.eval(impl, prediction, eval_results)

def print_results(eval_results):
    for metric in ['corrects', 'recranks']:
        if metric in eval_results:
            print metric, ':',
            print 1.0 * sum(eval_results[metric]) / len(eval_results[metric])

def main():
    db = DB_beans()
    NUM_SPLITS = 5
    all_trainable = get_trainable_data(db)
    all_algos = get_all_mentioned_algo(db)
    print all_trainable
    splits = split_data(all_trainable)
    trains = list(combinations(splits, NUM_SPLITS - 1))
    models = [None] * NUM_SPLITS
    # select classifier
    Classifier = RankingClassifier

    eval_results = Classifier.init_results()

    for i in range(NUM_SPLITS):
        model = models[i] = Classifier(extract_features, all_algos)
        train_data = list(chain(*trains[i]))
        valid_data = splits[NUM_SPLITS - 1 - i]

        print "Training Set:", len(train_data)
        print "Validation Set:", len(valid_data)

        print "Training..."
        model.train(train_data)

        print "Model:"
        print model.print_model()

        print "Verifying..."

        validation(model, valid_data, eval_results)

    print "Models:"
    for m in models:
        model.print_model()
    print "Results:"
    print_results(eval_results)

if __name__ == '__main__':
    main()
