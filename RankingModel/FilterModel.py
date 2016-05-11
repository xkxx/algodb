from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from ModelBase import ModelBase
from utils import is_positive, init_f1_metrics, export_tree

class FilterModel(ModelBase):
    def __init__(self, extract_features, all_algos, base=GaussianNB,
            num_neg=1, limit_features=[],
            use_pairwise_features=True, pairwise_limit_features=None):
        super(FilterModel, self).__init__(extract_features, all_algos, base, num_neg, limit_features)
        # store params
        self.model = None
        self.use_pairwise_features = use_pairwise_features
        self.pairwise_limit_features = pairwise_limit_features

    def clone(self):
        return FilterModel(self._extract_features, self.all_algos, self.BaseModel,
            self.num_neg, self.limit_features,
            self.use_pairwise_features, self.pairwise_limit_features)

    def _get_feature_vector(self, impl, algo):
        feature_vector = self._extract_features(impl, algo,
            limit_features=self.limit_features)
        if self.use_pairwise_features:
            for algo in self.all_algos:
                feature_vector.extend(self._extract_features(impl, algo, self.pairwise_limit_features))
        return feature_vector

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
            return (candidates,)
        else:
            return (None,)

    @staticmethod
    def init_results():
        return init_f1_metrics()

    def eval(self, sample, prediction, eval_results):
        (guess,) = prediction
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

    def print_model(self):
        print '  Model: ', repr(self.model)
        # TODO: print model internal dynamically
        # print '  Tree exported.'
        # export_tree(self.model)
