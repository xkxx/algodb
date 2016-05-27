import random
from utils import is_positive, print_f1

from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVR

from collections import namedtuple

class Prediction(namedtuple('Prediction', ['output', 'raw_scores', 'input'])):
    def __new__(_cls, output, raw_scores=None, input=None):
        return super(Prediction, _cls).__new__(_cls, output, raw_scores, input)

# abstract base class of Models
class ModelBase(object):
    def __init__(self, extract_features, all_algos, base, num_neg, limit_features, skip, model_refs):
        # store params
        self.all_algos = all_algos
        self._extract_features = extract_features
        self.BaseModel = base
        self.num_neg = num_neg
        self.limit_features = limit_features
        self.model_refs = model_refs
        self.model = None
        self.skip = skip
        self.feature_names = None

    def _get_feature_dict(self, impl, algo):
        return self._extract_features(impl, algo, self.limit_features)

    def _get_feature_vector(self, impl, algo):
        feature_dict = self._get_feature_dict(impl, algo)
        if self.feature_names is None:
            self.feature_names = feature_dict.keys()
        return feature_dict.values()

    def _create_training_vectors(self, data):
        # feature vector
        feature_vector = list()
        # score vector
        score_vector = list()
        algo_names = self.all_algos

        CORRESPONDING = 1.0
        NON_CORRESPONDING = 0.0

        for task in data:
            if is_positive(task):
                # positive training example
                feature_vector.append(self._get_feature_vector(task, task.label))
                score_vector.append(CORRESPONDING)

            # negative training example
            for i in range(self.num_neg):
                random_algo = None
                while (random_algo is None or random_algo == task.label):
                    random_algo = random.choice(algo_names)
                feature_vector.append(self._get_feature_vector(task, random_algo))
                score_vector.append(NON_CORRESPONDING)

        return (feature_vector, score_vector)

    @staticmethod
    def print_results(eval_results):
        """
        assume all metrics needs percentage calc
        """
        for metric in eval_results:
            print '  ', metric, ':\t',
            print 1.0 * sum(eval_results[metric]) / len(eval_results[metric])
        if 'true-positive' in eval_results:
            print_f1(eval_results)

    def classify(self, sample, candidates):
        """
            input: (sample, candidates)

            sample:
                the impl to classify
            candidates:
                algo | [algo] | None, depending on the output of the last model
                every model must be able to handle [algo] and None
                a threshold-type model must be able to handle algo

            return: (result, ...diagnostic_data)

            result:
                algo | [algo] | None, depending on the op of the model
            diagnostic_data:
                data used for self-eval later down the line
        """
        raise NotImplementedError()

    def train(self, data):
        raise NotImplementedError()

    def eval(self, sample, prediction, eval_results):
        raise NotImplementedError()

    def clone(self):
        "Create a clone of itself, without the trained state"
        raise NotImplementedError()

    def print_model(self):
        print '  Model: ', repr(self.model)
        feature_weights = None
        if isinstance(self.model, GaussianNB):
            print "  Priors: ", self.model.class_prior_
            feature_weights = self.model.theta_[1]
        elif (isinstance(self.model, LinearSVR) or
              isinstance(self.model, LogisticRegression)):
            feature_weights = self.model.coef_

        if feature_weights is not None:
            feature_weights_sorted = sorted(
                zip(self.feature_names, feature_weights),
                key=lambda (k, v): v,
                reverse=True)
            print "  Feature Weights: ", feature_weights_sorted

    def __str__(self):
        return ".%s(%s)." % (self.__class__.__name__, self.BaseModel.__name__)

    def __repr__(self):
        return self.__str__()
