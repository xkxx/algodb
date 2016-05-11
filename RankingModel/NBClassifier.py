import random
from sklearn.naive_bayes import GaussianNB
# ranking
from collections import Counter

class NBClassifier:
    def __init__(self, extract_features, all_algos):
        self.NBModel = None
        self.all_algos = all_algos
        self._extract_features = extract_features
        self._create_algo_mappings()

    def _create_algo_mappings(self):
        self.idx2algo = self.all_algos[:]
        self.idx2algo.append(None)
        self.algo2idx = {
            self.idx2algo[idx]: idx for idx in range(len(self.idx2algo))}

    def _create_nb_features(self, sample):
        features = []
        for algo in self.all_algos:
            features.extend(self._extract_features(sample, algo))
        return features

    def _create_training_vectors(self, data):
        feature_vector = list()
        label_vector = list()

        for task in data:
            feature_vector.append(self._create_nb_features(task))
            label = task.label if task.is_algo else None
            label_vector.append(self.algo2idx[label])

        return (feature_vector, label_vector)

    def train(self, data):
        (feature_vector, label_vector) = self._create_training_vectors(data)
        clf = GaussianNB()
        # train
        clf.fit(feature_vector, label_vector)
        self.NBModel = clf

    def classify(self, sample):
        [result] = self.NBModel.predict([self._create_nb_features(sample)])
        return (self.idx2algo[result],)

    @staticmethod
    def init_results():
        return {
            'corrects': []
        }

    def eval(self, sample, prediction, eval_results):
        pass

    def print_model(self):
        print "Priors: ", self.NBModel.class_prior_
        print 'Theta: ', self.NBModel.theta_
