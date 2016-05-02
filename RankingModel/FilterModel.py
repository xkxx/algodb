from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from ModelBase import ModelBase
from utils import is_positive

class FilterModel(ModelBase):
    def __init__(self, extract_features, all_algos,
            num_neg=1, base=GaussianNB, limit_features=[]):
        super(FilterModel, self).__init__(extract_features, all_algos, num_neg, limit_features)
        # store params
        self.model = None
        self.BaseModel = base

    def clone(self):
        return FilterModel(self._extract_features, self.all_algos,
            self.num_neg, self.BaseModel, self.limit_features)

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
        print 'sample:', sample

        features = self._get_feature_vector(sample, None)
        print 'feature:', features

        if self.model.predict([features]) == 1:
            return (candidates,)
        else:
            return (None,)

    @staticmethod
    def init_results():
        return {
            'true-positive': [0],
            'false-positive': [0],
            'true-negative': [0],
            'false-negative': [0]
        }

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

        print '  Filter:', result_class
        eval_results[result_class][0] += 1

    def print_model(self):
        print '  Model: ', repr(self.model)
        print "  Tree: ", self.model.tree_
