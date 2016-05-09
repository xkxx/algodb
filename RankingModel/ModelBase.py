import random
from utils import is_positive

# abstract base class of Models
class ModelBase(object):
    def __init__(self, extract_features, all_algos, base, num_neg, limit_features):
        # store params
        self.all_algos = all_algos
        self._extract_features = extract_features
        self.BaseModel = base
        self.num_neg = num_neg
        self.limit_features = limit_features

    def _get_feature_vector(self, impl, algo):
        return self._extract_features(impl, algo, self.limit_features)

    def _create_training_vectors(self, data):
        # feature vector
        feature_vector = list()
        # score vector
        score_vector = list()
        algo_names = self.all_algos

        CORRESPONDING = 1.0
        NON_CORRESPONDING = 0.0

        for task in data:
            if is_positive(task):
                # positive training example
                feature_vector.append(self._get_feature_vector(task, task.label))
                score_vector.append(CORRESPONDING)

            # negative training example
            for i in range(self.num_neg):
                random_algo = None
                while (random_algo is None or random_algo == task.label):
                    random_algo = random.choice(algo_names)
                feature_vector.append(self._get_feature_vector(task, random_algo))
                score_vector.append(NON_CORRESPONDING)

        return (feature_vector, score_vector)

    @staticmethod
    def print_results(eval_results):
        """
        assume all metrics needs percentage calc
        """
        for metric in eval_results:
            print '  ', metric, ':\t',
            print 1.0 * sum(eval_results[metric]) / len(eval_results[metric])

    def classify(self, sample, candidates):
        """
            input: (sample, candidates)

            sample:
                the impl to classify
            candidates:
                algo | [algo] | None, depending on the output of the last model
                every model must be able to handle [algo] and None
                a threshold-type model must be able to handle algo

            return: (result, ...diagnostic_data)

            result:
                algo | [algo] | None, depending on the op of the model
            diagnostic_data:
                data used for self-eval later down the line
        """
        raise NotImplementedError()

    def train(self, data):
        raise NotImplementedError()

    def eval(self, sample, prediction, eval_results):
        raise NotImplementedError()

    def print_model(self):
        raise NotImplementedError()

    def clone(self):
        "Create a clone with itself, without the trained state"
        raise NotImplementedError()

    def __str__(self):
        return ".%s." % (self.__class__.__name__)

    def __repr__(self):
        return self.__str__()
