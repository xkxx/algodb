from configParser import threshold_patch

class ModelWorkflow:
    def __init__(self, models):
        self.workflow = models

    def train(self, train_data):
        for model in self.workflow:
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
            cur = prediction[0]
        return (cur, predictions)

    def init_results(self):
        return [model.init_results() for model in self.workflow]

    def eval(self, sample, prediction, eval_results):
        (final_result, predictions) = prediction
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
        newworkflow = [model.clone() for model in self.workflow]
        # monkey patching
        threshold_patch(newworkflow)
        return ModelWorkflow(newworkflow)
