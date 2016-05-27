from sklearn.tree import DecisionTreeClassifier
from ModelBase import ModelBase, Prediction
from utils import is_positive, init_f1_metrics

class ThresholdModel(ModelBase):
    def __init__(self, extract_features, all_algos, base=DecisionTreeClassifier,
            num_neg=1, use_rank_score=True, use_nb_score=False,
            limit_features=[], skip=False, model_refs=None):
        super(ThresholdModel, self).__init__(extract_features, all_algos, base,
            num_neg, limit_features, skip, model_refs)
        # store params
        self.use_rank_score = use_rank_score
        self.use_nb_score = use_nb_score

    def clone(self):
        return ThresholdModel(self._extract_features, self.all_algos, self.BaseModel,
            self.num_neg, self.use_rank_score, self.use_nb_score,
            self.limit_features, self.skip, self.model_refs)

    def _get_feature_dict(self, impl, algo):
        feature_dict = self._extract_features(impl, algo,
            limit_features=self.limit_features)
        if self.use_rank_score:
            assert 'RankingModel' in self.model_refs
            rankingModel = self.model_refs['RankingModel']
            (_, all_ranks) = rankingModel.classify(impl, candidates=[algo])
            feature_dict['rank_score'] = all_ranks[0][1]
        if self.use_nb_score:
            assert 'BinaryNBModel' in self.model_refs
            rankingModel = self.model_refs['BinaryNBModel']
            [nb_feature] = rankingModel.get_log_prob(impl, [algo])
            feature_dict['nb_score'] = nb_feature
        return feature_dict

    def _train_threshold(self, feature_vector, score_vector):
        params = {}
        if self.BaseModel == DecisionTreeClassifier:
            # special convinient params for decision tree
            params = {'max_depth': len(feature_vector[0]), 'presort': True}

        clf = self.BaseModel(**params)
        clf.fit(feature_vector, score_vector)
        self.model = clf

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
        prediction = self.model.predict([features]) == 1

        return Prediction(output=candidate if prediction else None, input=candidate)

    @staticmethod
    def init_results():
        metrics = init_f1_metrics()
        metrics.update({
            'wrong-negative': [0],
            'wrong-positive': [0]
        })
        return metrics

    def eval(self, sample, prediction, eval_results):
        (guess, candidate) = (prediction.output, prediction.input)
        result_class = None
        if candidate is None:
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
