import random


class RankingClassifier:
    def __init__(self, extract_features, all_algos, num_neg=1):
        self.rankingModel = None
        self.thresholdModel = None
        self.all_algos = all_algos
        self._extract_features = extract_features
        self.num_neg = num_neg

    def _create_training_vectors(self, data):
        # feature vector
        feature_vector = list()
        # score vector
        score_vector = list()
        algo_names = self.all_algos

        CORRESPONDING = 1.0
        NON_CORRESPONDING = 0.0

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
                feature_vector.append(extract_features(task, random_algo))
                score_vector.append(NON_CORRESPONDING)

        return (feature_vector, score_vector)

    def _train_ranking(self, feature_vector, score_vector):
        clf = svm.LinearSVR()
        # train
        clf.fit(feature_vector, score_vector)
        self.rankingModel = clf

    def _train_threshold(self, feature_vector, score_vector):
        # all_algos = get_all_mentioned_algo(db)
        # feature vector
        stump_features = list()
        # score vector
        stump_scores = list()
        # first try rank training set on trained model
        predictions = self.rankingModel.predict(feature_vector)
        # then train decision stump
        stump_features = [[x] for x in predictions]
        stump_scores = [1 if score == 1 else -1 for score in score_vector]

        clf = DecisionTreeClassifier()
        clf.fit(stump_features, stump_scores)
        self.thresholdModel = clf

    def train(self, data):
        (feature_vector, score_vector) = self._create_training_vectors(data, self.all_algos)
        # first train ranking model
        ranking = train_ranking(feature_vector, score_vector)
        threshold = train_threshold(feature_vector, score_vector)

    def _classify_rank(self, sample):
        ranks = Counter()
        for cand in candidates:
            sample_features = self._extract_features(sample, cand)
            [result] = rankingModel.predict([sample_features])
            ranks[cand] = result
        return ranks.most_common()

    def classify(sample):
        (ranking, threshold) = model
        results = self._classify_rank(sample)
        (topcand, toprank) = results[0]
        guess = None
        if threshold.predict([[toprank]]) == 1:
            guess = topcand
        return (guess, results)

    def init_results(self):
        return {
            'corrects': 0,
            'recranks': []
        }

    def eval(self, sample, guess, results):
        (guess, result) = guess
        keys = zip(*result)[0]
        print "Top Rank:", result[0:3]
        rank = None
        if sample.label is None:
            if guess == sample.label:
                rank = 1
            else:
                rank = 1 + len(self.all_algos)
        else:
            rank = keys.index(sample.label) + 1
        print "Rank of Correct Algo:", rank
        results['recranks'].append(1.0 / rank)

    def print_model(self):
        print "Coefs: ", self.rankingModel._coefs
        print "Threshold: ", self.thresholdModel._tree
