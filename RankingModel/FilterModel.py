from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from ModelBase import ModelBase, Prediction
from utils import is_positive, init_f1_metrics

class FilterModel(ModelBase):
    def __init__(self, extract_features, all_algos, base=GaussianNB,
            num_neg=1, limit_features=[], skip=False, model_refs=None,
            use_pairwise_features=True, pairwise_limit_features=None,
            use_rank_score=False, use_nb_score=False):
        super(FilterModel, self).__init__(extract_features, all_algos, base,
            num_neg, limit_features, skip, model_refs)
        # store params
        self.use_pairwise_features = use_pairwise_features
        self.pairwise_limit_features = pairwise_limit_features
        self.use_rank_score = use_rank_score
        self.use_nb_score = use_nb_score

    def clone(self):
        return FilterModel(self._extract_features, self.all_algos, self.BaseModel,
            self.num_neg, self.limit_features, self.skip, self.model_refs,
            self.use_pairwise_features, self.pairwise_limit_features,
            self.use_rank_score, self.use_nb_score)

    def _get_feature_dict(self, impl, algo):
        feature_dict = self._extract_features(impl, algo,
            limit_features=self.limit_features)
        all_algos = self.all_algos
        if self.use_pairwise_features:
            for algo in self.all_algos:
                feature_dict.update(
                    self._extract_features(impl, algo,
                        limit_features=self.pairwise_limit_features,
                        feature_name_prefix=algo.title + ':'))

        if self.use_rank_score:
            assert 'RankingModel' in self.model_refs
            rankingModel = self.model_refs['RankingModel']
            rank_scores = rankingModel.get_rank_scores(impl, all_algos)
            for i in range(len(all_algos)):
                feature_dict['%s:rank_score' % all_algos[i]] = rank_scores[i]

        if self.use_nb_score:
            assert 'BinaryNBModel' in self.model_refs
            nbModel = self.model_refs['BinaryNBModel']
            nb_features = nbModel.get_log_prob(impl, all_algos)
            for i in range(len(all_algos)):
                feature_dict['%s:nb_score' % all_algos[i]] = nb_features[i]
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

    def classify(self, sample, candidates):
        assert candidates is not None and type(candidates) == list

        features = self._get_feature_vector(sample, None)

        if self.model.predict([features]) == 1:
            return Prediction(output=candidates)
        else:
            return Prediction(output=None)

    @staticmethod
    def init_results():
        return init_f1_metrics()

    def eval(self, sample, prediction, eval_results):
        guess = prediction.output
        guess_is_algo = guess is not None
        result_class = None

        if is_positive(sample):
            if guess_is_algo:
                result_class = 'true-positive'
            else:
                result_class = 'false-negative'
        else:
            if guess_is_algo:
                result_class = 'false-positive'
            else:
                result_class = 'true-negative'

        print '  Filter:', guess_is_algo
        print '  Class:', result_class
        eval_results[result_class][0] += 1
