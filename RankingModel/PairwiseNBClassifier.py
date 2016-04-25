import random
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
# ranking
from collections import Counter

class PairwiseNBClassifier:
    def __init__(self, extract_features, all_algos, num_neg=1):
        self.NBModel = None
        self.all_algos = all_algos
        self._extract_features = extract_features
        self.num_neg = num_neg

    def _create_training_vectors(self, data):
        # feature vector
        feature_vector = list()
        # score vector
        score_vector = list()
        algo_names = self.all_algos

        CORRESPONDING = 1
        NON_CORRESPONDING = 0

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

    def classify(self, sample):
        positives = []
        for cand in self.all_algos:
            sample_features = self._extract_features(sample, cand)
            [result] = self.NBModel.predict([sample_features])
            prob = self.NBModel.predict_log_proba([sample_features])[0][1]  # prob of positive
            if result == 1:
                positives.append((prob, cand))
        if len(positives) == 0:
            return (None, positives)
        # pick best positive
        sorted_positive = sorted(positives)
        best = positives[0][1]  # cand
        return (best, positives)

    def _train(self, data):
        (feature_vector, score_vector) = \
            self._create_training_vectors(data)
        clf = GaussianNB()
        # train
        clf.fit(feature_vector, score_vector)
        self.NBModel = clf

    def train(self, data):
        self._train(data)

    @staticmethod
    def init_results():
        return {
            'corrects': [],
            'in-positive-set': [],
            'false-positive': []
        }

    def eval(self, sample, prediction, eval_results):
        (best, cands) = prediction
        if sample.label is not None:
            if len(cands) == 0:
                eval_results['in-positive-set'].append(0)
            else:
                (_, found_algos) = zip(*cands)
                eval_results['in-positive-set'].append(
                    int(sample.label in found_algos))
        else:
            eval_results['false-positive'].append(int(len(cands) > 0))

        print "Candidates: ", cands

    def print_model(self):
        print "Priors: ", self.NBModel.class_prior_
        print 'Theta: ', self.NBModel.theta_
