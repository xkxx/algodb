from sklearn.naive_bayes import GaussianNB
from ModelBase import ModelBase

class BinaryNBModel(ModelBase):
    def __init__(self, extract_features, all_algos, num_neg=1, limit_features=None):
        super(BinaryNBModel, self).__init__(extract_features, all_algos, num_neg, limit_features)
        self.model = None

    def clone(self):
        return BinaryNBModel(self._extract_features, self.all_algos,
            self.num_neg, self.limit_features)

    def classify(self, sample):
        positives = []
        for cand in self.all_algos:
            sample_features = self._extract_features(sample, cand)
            [result] = self.model.predict([sample_features])
            # prob = self.model.predict_log_proba([sample_features])[0][1]  # prob of positive
            if result == 1:
                positives.append(cand)
        return (positives,)

    def _train(self, data):
        (feature_vector, score_vector) = \
            self._create_training_vectors(data)
        clf = GaussianNB()
        # train
        clf.fit(feature_vector, score_vector)
        self.model = clf

    def train(self, data):
        self._train(data)

    @staticmethod
    def init_results():
        return {
            'in-positive-set': []
        }

    def eval(self, sample, prediction, eval_results):
        (positive,) = prediction
        if sample.label is not None and sample.is_algo:
            if len(positive) == 0:
                eval_results['in-positive-set'].append(0)
            else:
                eval_results['in-positive-set'].append(
                    int(sample.label in positive))

        print "  Candidates: ", positive

    def print_model(self):
        print 'Model: ', repr(self.model)
        print "  Priors: ", self.model.class_prior_
        print '  Theta: ', self.model.theta_
