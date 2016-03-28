import random
from sklearn.naive_bayes import GaussianNB
# ranking
from collections import Counter

class SpreadNBClassifier:
    def __init__(self, extract_features, all_algos):
        self.NBModel = None
        self.all_algos = all_algos
        self._extract_features = extract_features

    def _create_algo_mappings(self):
        self.idx2algo = self.all_algos[:]
        self.idx2algo.append(None)
        self.algo2idx = {
            self.idx2algo[idx]: idx for idx in range(len(self.idx2algo))}

    def _create_training_vectors(self, data):
        # feature vector
        feature_vector = list()
        # score vector
        score_vector = list()
        all_algos = self.all_algos

        for task in data:
            features = []
            for algo in all_algos:
                features.extend(self._extract_features(task, algo))
            feature_vector.append(features)
            score_vector.append(self.algo2idx[algo])

        return (feature_vector, score_vector)

    def train(self, data):
        (feature_vector, score_vector) = self._create_training_vectors(data)
        clf = GaussianNB()
        # train
        clf.fit(feature_vector, score_vector)
        self.NBModel = clf

    def _classify_rank(self, sample):
        ranks = Counter()
        candidates = self.all_algos

        for cand in candidates:
            sample_features = self._extract_features(sample, cand)
            [result] = self.rankingModel.predict([sample_features])
            ranks[cand] = result
        return ranks.most_common()

    def classify(self, sample):
        results = self._classify_rank(sample)
        (topcand, toprank) = results[0]
        guess = None
        if self.thresholdModel.predict([[toprank]]) == 1:
            guess = topcand
        return (guess, results)

    @staticmethod
    def init_results():
        return {
            'corrects': [],
            'recranks': []
        }

    def eval(self, sample, prediction, results):
        (guess, result) = prediction
        keys = zip(*result)[0]
        print "Top Rank:", result[0:3]
        rank = None
        if sample.label is None:
            if guess == sample.label:
                rank = 1
            else:
                rank = 1 + len(self.all_algos)
        else:
            rank = keys.index(sample.label) + 1
        print "Rank of Correct Algo:", rank
        results['recranks'].append(1.0 / rank)

    def print_model(self):
        print "Coef: ", self.rankingModel.coef_
        print "Threshold: ", self.thresholdModel.tree_
