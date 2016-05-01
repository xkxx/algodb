# for utf8 encoding and decoding
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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

# parsing arguments and config
import argparse
from configParser import read_config, get_models, load_models
from workflow import ModelWorkflow

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--balanced_train', '-bt', action="store_true",
        dest="balanced_train", default=argparse.SUPPRESS)
    parser.add_argument('--balanced_dev', '-bd', action="store_true",
        dest="balanced_test", default=argparse.SUPPRESS)
    parser.add_argument('config_file', action="store", nargs=1)

    args = parser.parse_args(sys.argv[1:])

    if not args.config_file:
        parser.print_help()
        sys.exit(1)
    return args

# return [(impl, corres_algo)]
def get_trainable_data(db):
    return get_all_tasks(db)

def split_data(data, k):
    per_split = (len(data) + k - 1) / k

    splits = []
    for i in range(k):
        cur_start = i * per_split
        left = len(data) - cur_start
        splits.append(data[cur_start:(cur_start + min(per_split, left))])
    return splits

def create_eval_stats(model):
    return ({
        'corrects': []
    }, model.init_results())

def print_results(model, eval_results):
    (overall_stats, specific_stats) = eval_results
    corrects = overall_stats['corrects']
    print "Overall Accuracy: ", 1.0 * sum(corrects) / len(corrects)
    print "Model Specific Stats:\n"
    model.print_results(eval_results)

def validation(model, samples, eval_results):
    (overall_stats, specific_stats) = eval_results
    for impl in samples:
        print "Impl:", impl
        print "Algo:", impl.label
        prediction = model.classify(impl)
        guess = prediction[0]
        print "Prediction:", guess
        overall_stats['corrects'].append(guess == impl.label)
        # classifier-defined metrics
        model.eval(impl, prediction, specific_stats)

def inject_sample_experiment(samples):
    none_count = 0
    filtered = []
    for impl in samples:
        if not impl.is_algo or impl.label is None:
            if none_count > 0:
                continue
            none_count += 1
        filtered.append(impl)
    return filtered
    # return samples

def main(config):
    # init data
    db = DB_beans()
    all_trainable = get_trainable_data(db)
    all_algos = get_all_mentioned_algo(db)
    extract_features = extract_features_factory(db)
    print all_trainable
    # split data
    NUM_SPLITS = config['num_splits']
    splits = split_data(all_trainable, NUM_SPLITS)
    trains = list(combinations(splits, NUM_SPLITS - 1))
    # init models
    models = [None] * NUM_SPLITS
    workflow = ModelWorkflow(
        load_models(config, extract_features, all_algos))
    eval_stats = create_eval_stats(workflow)

    for i in range(NUM_SPLITS):
        model = models[i] = workflow.clone()
        train_data = list(chain(*trains[i]))
        valid_data = splits[NUM_SPLITS - 1 - i]

        if config['balanced_train']:
            train_data = inject_sample_experiment(train_data)
        if config['balanced_test']:
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
    print_results(workflow, eval_stats)

if __name__ == '__main__':
    args = parseArgs()
    main(read_config(args.config_file[0], vars(args)))
