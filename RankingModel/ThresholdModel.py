import random
# using support vector regression: features -> ranking score
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
# ranking
from collections import Counter

class ThresholdModel:
    def __init__(self, extract_features, all_algos, rankingModel,
            num_neg=1, base=DecisionTreeClassifier):
        self.rankingModel = rankingModel
        self.thresholdModel = None
        self.BaseModel = base
        self.all_algos = all_algos
        self._extract_features = extract_features
        self.num_neg = num_neg

    def get_feature_vector(self, impl, algo):
        return self.rankingModel.predict([self._extract_features(impl, algo)])

    def _create_training_vectors(self, data):
        # feature vector
        feature_vector = []
        # score vector
        score_vector = []
        algo_names = self.all_algos

        CORRESPONDING = 1.0
        NON_CORRESPONDING = 0.0

        for task in data:
            if task.label is not None and task.is_algo:
                # positive training example
                feature_vector.append(self.get_feature_vector(task, task.label))
                score_vector.append(CORRESPONDING)

            # negative training example
            for i in range(self.num_neg):
                random_algo = None
                while (random_algo is None or random_algo == task.label):
                    random_algo = random.choice(algo_names)
                feature_vector.append(self.get_feature_vector(task, random_algo))
                score_vector.append(NON_CORRESPONDING)

        return (feature_vector, score_vector)

    def _train_threshold(self, feature_vector, score_vector):
        clf = self.BaseModel(max_depth=2, presort=True)
        clf.fit(feature_vector, score_vector)
        self.thresholdModel = clf

    def train(self, data):
        (feature_vector, score_vector) = self._create_training_vectors(data)
        # first train ranking model
        self._train_threshold(feature_vector, score_vector)

    def classify(self, sample, candidate):
        features = [self.get_feature_vector(sample, candidate)]
        guess = None

        if self.thresholdModel.predict([features]) == 1:
            guess = candidate
        return (guess, candidate)

    @staticmethod
    def init_results():
        return {
            'corrects': [],
            'true-positive': [0],
            'false-positive': [0],
            'true-negative': [0],
            'false-negative': [0],
            'wrong-top-cand': [0]
        }

    def eval(self, sample, prediction, eval_results):
        (guess, candidate) = prediction

        if sample.label is None:
            # candidate must be wrong
            if guess is None:
                eval_results['true-negative'][0] += 1
            else:
                eval_results['false-positive'][0] += 1
        # sample.label is not None
        elif sample.label == candidate:
            if guess is None:
                eval_results['false-negative'][0] += 1
            else:  # guess == sample.label
                eval_results['true-positive'][0] += 1
        else:  # candidate is wrong
            if guess is None:
                eval_results['none|wrong-cand'][0] += 1
            else:  # guess is not None
                eval_results['wrong|wrong-cand'][0] += 1

    def print_model(self):
        print "Threshold: ", self.thresholdModel.tree_
