class ModelWorkflow:
    def __init__(self, models):
        self.workflow = models

    def train(self, train_data):
        for model in self.workflow:
            model.train_data()

    def classify(self, sample):
        predictions = []
        cur = []  # [] is a poor man's `maybe` #monad
        for model in self.workflow:
            # each model takes at most 2 params:
            # 1: the sample to classify
            # 2: an optional intermediate val from the last model
            classify_input = [sample] + cur
            prediction = model.classify(*classify_input)
            # each model returns n values in a tuple:
            # 1: the final prediction, or intermediate val to the next model
            # rest: info needed for eval
            predictions.append(prediction)
            cur = [prediction[0]]
        return (cur[0], predictions)

    def init_results(self):
        return [model.init_results() for model in self.workflow]

    def eval(self, sample, prediction, eval_results):
        (final_result, predictions) = prediction
        for i in range(len(self.workflow)):
            self.workflow[i].eval(sample, predictions[i], eval_results[i])

    def print_results(self, eval_results):
        for i in range(len(self.workflow)):
            model = self.workflow[i]
            print model.__name__, ':'
            model.print_results(eval_results[i])

    def print_model(self):
        for model in self.workflow:
            print model.__class__.__name__, ':'
            model.print_model()

    def clone(self):
        newworkflow = [model.clone() for model in self.workflow]
        return ModelWorkflow(newworkflow)
