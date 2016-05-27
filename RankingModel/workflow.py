from configParser import models_patch
from ModelBase import Prediction

class ModelWorkflow:
    def __init__(self, models):
        self.models = models
        # if model specifies 'skip', they should be skipped during eval
        # it's necessary if they are only used as part of other models
        self.workflow = [m for m in models if not m.skip]

    def train(self, train_data):
        train_order = {
            'BinaryNBModel': 1,
            'RankingModel': 2,
            'FilterModel': 3,
            'ThresholdModel': 4}

        models = sorted(self.models,
            key=lambda x: train_order[x.__class__.__name__])

        for model in models:
            model.train(train_data)

    def classify(self, sample, candidates):
        predictions = []
        cur = candidates
        for model in self.workflow:
            # each model takes at most 2 params:
            # 1: the sample to classify
            # 2: an intermediate val from the last model
            prediction = model.classify(sample, cur)
            # each model returns n values in a tuple:
            # 1: the final prediction, or intermediate val to the next model
            # rest: info needed for eval
            predictions.append(prediction)
            # print predictions
            # print type(model)
            # print
            cur = prediction.output
        return Prediction(output=cur, raw_scores=predictions)

    def init_results(self):
        return [model.init_results()
            for model in self.workflow
            if not model.skip]

    def eval(self, sample, prediction, eval_results):
        predictions = prediction.raw_scores
        for i in range(len(self.workflow)):
            self.workflow[i].eval(sample, predictions[i], eval_results[i])

    def print_results(self, eval_results):
        for i in range(len(self.workflow)):
            model = self.workflow[i]
            print model, ':'
            model.print_results(eval_results[i])
            print

    def __str__(self):
        return '{Workflow: %s}' % ('->'.join([str(model) for model in self.workflow]))

    def __repr__(self):
        return self.__str__()

    def print_model(self):
        for model in self.workflow:
            print model, ':'
            model.print_model()

    def clone(self):
        newmodels = [model.clone() for model in self.models]
        # monkey patching
        models_patch(newmodels)
        return ModelWorkflow(newmodels)
