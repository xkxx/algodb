import random
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
# ranking
from collections import Counter

class RankingNBClassifier:
    def __init__(self, extract_features, all_algos, num_neg=1):
        self.NBModel = None
        self.all_algos = all_algos
        self._extract_features = extract_features
        self.num_neg = num_neg
        self._create_algo_mappings()

    def _create_algo_mappings(self):
        self.idx2algo = self.all_algos[:]
        self.idx2algo.append(None)
        self.algo2idx = {
            self.idx2algo[idx]: idx for idx in range(len(self.idx2algo))}

    def _create_ranking_training_vectors(self, data):
        # feature vector
        feature_vector = list()
        # score vector
        score_vector = list()
        algo_names = self.all_algos

        CORRESPONDING = 1.0
        NON_CORRESPONDING = 0.0

        for task in data:
            if task.label is not None and task.is_algo:
                # positive training example
                feature_vector.append(self._extract_features(task, task.label))
                score_vector.append(CORRESPONDING)

            # negative training example
            for i in range(self.num_neg):
                random_algo = None
                while (random_algo is None or random_algo == task.label):
                    random_algo = random.choice(algo_names)
                feature_vector.append(self._extract_features(task, random_algo))
                score_vector.append(NON_CORRESPONDING)

        return (feature_vector, score_vector)

    def _create_nb_features(self, sample):
        features = []
        for algo in self.all_algos:
            [score] = self.rankingModel.predict(
                [self._extract_features(sample, algo)])
            features.append(score)
        return features

    def _create_nb_training_vectors(self, data):
        feature_vector = list()
        label_vector = list()

        for task in data:
            feature_vector.append(self._create_nb_features(task))
            label = task.label if task.is_algo else None
            label_vector.append(self.algo2idx[label])

        return (feature_vector, label_vector)

    def _train_ranking(self, data):
        (feature_vector, score_vector) = \
            self._create_ranking_training_vectors(data)
        clf = svm.LinearSVR()
        # train
        clf.fit(feature_vector, score_vector)
        self.rankingModel = clf

    def _train_nb(self, data):
        (feature_vector, label_vector) = \
            self._create_nb_training_vectors(data)
        clf = GaussianNB()
        # train
        clf.fit(feature_vector, label_vector)
        self.NBModel = clf

    def train(self, data):
        self._train_ranking(data)
        self._train_nb(data)

    def classify(self, sample):
        [result] = self.NBModel.predict([self._create_nb_features(sample)])
        return (self.idx2algo[result],)

    @staticmethod
    def init_results():
        return {
            'corrects': []
        }

    def eval(self, sample, prediction, results):
        pass

    def print_model(self):
        print "Coef: ", self.rankingModel.coef_
        print "Priors: ", self.NBModel.class_prior_
        print 'Theta: ', self.NBModel.theta_
