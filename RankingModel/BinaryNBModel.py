from sklearn.naive_bayes import GaussianNB
from ModelBase import ModelBase, Prediction
from utils import is_positive, init_f1_metrics

class BinaryNBModel(ModelBase):
    def __init__(self, extract_features, all_algos, base=GaussianNB,
            num_neg=1, limit_features=None, skip=False, model_refs=None):
        super(BinaryNBModel, self).__init__(extract_features, all_algos, base,
            num_neg, limit_features, skip, model_refs)

    def clone(self):
        return BinaryNBModel(self._extract_features, self.all_algos, self.BaseModel,
            self.num_neg, self.limit_features, self.skip, self.model_refs)

    def classify(self, sample, candidates):
        if candidates is None:
            return (None, [])
        assert type(candidates) == list
        # candidates = candidates if candidates is not None else self.all_algos
        positives = []
        raw_results = []
        for cand in candidates:
            sample_features = self._get_feature_vector(sample, cand)
            [result] = self.model.predict([sample_features])
            # prob = self.model.predict_log_proba([sample_features])[0][1]  # prob of positive
            # record this for eval
            raw_results.append((sample, cand, result))
            if result == 1:
                positives.append(cand)
        return Prediction(output=positives, raw_scores=raw_results)

    def get_log_prob(self, sample, candidates):
        raw_results = []
        for cand in candidates:
            sample_features = self._get_feature_vector(sample, cand)
            [result] = self.model.predict_log_proba([sample_features])
            raw_results.append(result[1])

        return raw_results

    def _train(self, data):
        (feature_vector, score_vector) = \
            self._create_training_vectors(data)
        clf = self.BaseModel()
        # train
        clf.fit(feature_vector, score_vector)
        self.model = clf

    def train(self, data):
        self._train(data)

    @staticmethod
    def init_results():
        metrics = init_f1_metrics()
        metrics.update({
            'size|positive': [],
            'size|negative': [],
            'in-positive-set': [],
            'non-empty|negative': []
        })
        return metrics

    def eval(self, sample, prediction, eval_results):
        (positive, raw_results) = (prediction.output, prediction.raw_scores)
        if positive is None:
            return
        print "  Candidates: ", positive
        # for computing f1
        for (_, cand, label) in raw_results:
            result_class = None
            if is_positive(sample) and cand == sample.label:
                if label == 1:
                    result_class = 'true-positive'
                else:
                    result_class = 'false-negative'
            else:
                if label == 1:
                    result_class = 'false-positive'
                else:
                    result_class = 'true-negative'
            eval_results[result_class][0] += 1

        if is_positive(sample):
            eval_results['size|positive'].append(len(positive))
            if len(positive) == 0:
                eval_results['in-positive-set'].append(0)
            else:
                print "  Correct result in positive set."
                eval_results['in-positive-set'].append(
                    int(sample.label in positive))
        else:
            eval_results['size|negative'].append(len(positive))
            eval_results['non-empty|negative'].append(int(len(positive) != 0))
