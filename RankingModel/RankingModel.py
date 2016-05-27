# using support vector regression: features -> ranking score
from sklearn.svm import LinearSVR
# ranking
from collections import Counter
from ModelBase import ModelBase, Prediction
from utils import is_positive

class RankingModel(ModelBase):
    def __init__(self, extract_features, all_algos, base=LinearSVR,
            num_neg=1, limit_features=None, use_nb_score=False, skip=False,
            model_refs=None):
        super(RankingModel, self).__init__(extract_features, all_algos, base,
            num_neg, limit_features, skip, model_refs)
        self.use_nb_score = use_nb_score

    def clone(self):
        return RankingModel(self._extract_features, self.all_algos, self.BaseModel,
            self.num_neg, self.limit_features, self.use_nb_score, self.skip,
            self.model_refs)

    def _get_feature_dict(self, impl, algo):
        feature_dict = self._extract_features(impl, algo,
            limit_features=self.limit_features)
        if self.use_nb_score:
            assert 'BinaryNBModel' in self.model_refs
            nbModel = self.model_refs['BinaryNBModel']
            [nb_feature] = nbModel.get_log_prob(impl, [algo])
            feature_dict['nb_score'] = nb_feature
        return feature_dict

    def _train_ranking(self, feature_vector, score_vector):
        clf = self.BaseModel()
        # train
        clf.fit(feature_vector, score_vector)
        self.model = clf

    def train(self, data):
        (feature_vector, score_vector) = self._create_training_vectors(data)
        # first train ranking model
        self._train_ranking(feature_vector, score_vector)

    def _classify_rank(self, sample, candidates):
        ranks = Counter()

        for cand in candidates:
            sample_features = self._get_feature_vector(sample, cand)
            [result] = self.model.predict([sample_features])
            ranks[cand] = result
        return ranks

    def get_rank_scores(self, sample, candidates):
        return self._classify_rank(sample, candidates).values()

    def classify(self, sample, candidates):
        if candidates is None:
            return (None, [])
        assert type(candidates) == list
        # print 'ranking:', candidates
        # candidates = candidates if candidates is not None else self.all_algos
        results = self._classify_rank(sample, candidates).most_common()
        if len(results) == 0:
            return (None, results)
        (topcand, toprank) = results[0]

        return Prediction(output=topcand, raw_scores=results)

    @staticmethod
    def init_results():
        return {
            'recranks': [],
            'correct|inset': []
        }

    def eval(self, sample, prediction, eval_results):
        (guess, result) = (prediction.output, prediction.raw_scores)

        if guess is not None:
            keys = zip(*result)[0] if len(result) != 0 else []
            if sample.label not in keys:
                print "  Correct label not in candidate set"
                return
            print "  Top Rank:", result[0:3]
            rank = keys.index(sample.label) + 1
            print "  Rank of Correct Algo:", rank
            eval_results['recranks'].append(1.0 / rank)
            eval_results['correct|inset'].append(sample.label == guess)
