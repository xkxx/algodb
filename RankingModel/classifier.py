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
from FeatureExtractor import extract_features_factory

from db_dependency import DB_beans

from itertools import chain, combinations

# models
from RankingThresholdClassifier import RankingThresholdClassifier
from NBClassifier import NBClassifier
from RankingNBClassifier import RankingNBClassifier
from PairwiseNBClassifier import PairwiseNBClassifier

# parsing command line arguments
import argparse

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
    for metric in ['corrects', 'recranks', 'in-positive-set', 'false-positive']:
        if metric in eval_results:
            print metric, ':',
            print 1.0 * sum(eval_results[metric]) / len(eval_results[metric])

def inject_sample_experiment(samples):
    none_count = 0
    filtered = []
    for impl in samples:
        #######
        if not impl.is_algo or impl.label is None:
            if none_count > 0:
                continue
            none_count += 1
        #######
        filtered.append(impl)
    return filtered
    # return samples

def main(Classifier, balanced_train, balanced_test):
    db = DB_beans()
    NUM_SPLITS = 5
    all_trainable = get_trainable_data(db)
    all_algos = get_all_mentioned_algo(db)
    extract_features = extract_features_factory(db)
    print all_trainable
    splits = split_data(all_trainable)
    trains = list(combinations(splits, NUM_SPLITS - 1))
    models = [None] * NUM_SPLITS

    eval_stats = Classifier.init_results()

    for i in range(NUM_SPLITS):
        model = models[i] = Classifier(extract_features, all_algos)
        train_data = list(chain(*trains[i]))
        valid_data = splits[NUM_SPLITS - 1 - i]

        if balanced_train:
            train_data = inject_sample_experiment(train_data)
        if balanced_test:
            valid_data = inject_sample_experiment(valid_data)

        print "Training Set:", len(train_data)
        print "Validation Set:", len(valid_data)

        print "Training..."
        model.train(train_data)

        print "Model:"
        print model.print_model()

        print "Verifying..."

        validation(model, valid_data, eval_stats)

    print "Models:"
    for m in models:
        model.print_model()
    print "Results:"
    print_results(eval_stats)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--classifier', '-c', action="store", dest="classifier", default="RankingClassifier")
    parser.add_argument('--balanced_train', '-bt', action="store_true", dest="balanced_train", default=False)
    parser.add_argument('--balanced_dev', '-bd', action="store_true", dest="balanced_test", default=False)
    args = parser.parse_args(sys.argv[1:])

    if args.classifier:
        main(eval(args.classifier), args.balanced_train, args.balanced_test)
    else:
        print parser.print_help()
