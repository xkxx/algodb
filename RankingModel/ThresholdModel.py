from sklearn.tree import DecisionTreeClassifier
from ModelBase import ModelBase
from utils import is_positive, init_f1_metrics

class ThresholdModel(ModelBase):
    def __init__(self, extract_features, all_algos, base=DecisionTreeClassifier,
            rankingModel=None, num_neg=1, use_rank_score=True, limit_features=[]):
        super(ThresholdModel, self).__init__(extract_features, all_algos, base, num_neg, limit_features)
        # store params
        self.rankingModel = rankingModel
        self.thresholdModel = None
        self.use_rank_score = use_rank_score

    def clone(self):
        return ThresholdModel(self._extract_features, self.all_algos, self.BaseModel,
            self.rankingModel, self.num_neg,
            self.use_rank_score, self.limit_features)

    def _get_feature_vector(self, impl, algo):
        feature_vector = self._extract_features(impl, algo,
            limit_features=self.limit_features)
        if self.use_rank_score:
            assert self.rankingModel is not None
            (_, all_ranks) = self.rankingModel.classify(impl, candidates=[algo])
            feature_vector.append(all_ranks[0][1])
        return feature_vector

    def _train_threshold(self, feature_vector, score_vector):
        params = {}
        if self.BaseModel == DecisionTreeClassifier:
            # special convinient params for decision tree
            params = {'max_depth': len(feature_vector[0]), 'presort': True}

        clf = self.BaseModel(**params)
        clf.fit(feature_vector, score_vector)
        self.thresholdModel = clf

    def train(self, data):
        (feature_vector, score_vector) = self._create_training_vectors(data)
        # first train ranking model
        self._train_threshold(feature_vector, score_vector)

    def classify(self, sample, candidate):
        assert type(candidate) != list
        if candidate is None:
            # nothing to do
            return (None, None)
        features = self._get_feature_vector(sample, candidate)
        prediction = self.thresholdModel.predict([features]) == 1

        return (candidate if prediction else None, candidate)

    @staticmethod
    def init_results():
        metrics = init_f1_metrics()
        metrics.update({
            'wrong-negative': [0],
            'wrong-positive': [0]
        })
        return metrics

    def eval(self, sample, prediction, eval_results):
        (guess, candidate) = prediction
        result_class = None
        if candidate == None:
            return
        # TODO: what if candidate is None?
        if not is_positive(sample):
            # candidate must be wrong
            if guess is None:
                result_class = 'true-negative'
            else:
                result_class = 'false-positive'
        # sample.label is not None
        elif sample.label == candidate:
            if guess is None:
                result_class = 'false-negative'
            else:  # guess == sample.label
                result_class = 'true-positive'
        else:  # candidate is wrong
            if guess is None:
                result_class = 'wrong-negative'
            else:  # guess is not None
                result_class = 'wrong-positive'

        print '  Threshold:', guess
        print '  Class:', result_class
        eval_results[result_class][0] += 1

    def print_model(self):
        print '  Model: ', repr(self.thresholdModel)
        print "  Threshold: ", self.thresholdModel.tree_
