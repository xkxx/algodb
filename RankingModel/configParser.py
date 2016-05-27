import json
from BinaryNBModel import BinaryNBModel
from RankingModel import RankingModel
from ThresholdModel import ThresholdModel
from FilterModel import FilterModel

from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVR

modelMap = {
    'BinaryNBModel': BinaryNBModel,
    'RankingModel': RankingModel,
    'ThresholdModel': ThresholdModel,
    'FilterModel': FilterModel
}

baseModelMap = {
    'DecisionTreeClassifier': DecisionTreeClassifier,
    'GaussianNB': GaussianNB,
    'LogisticRegression': LogisticRegression,
    'LinearSVR': LinearSVR
}

defaultConfig = {
    "balanced_train": False,
    "balanced_test": False,
    "num_splits": 5,
    "workflow": []
}

def read_config(filename, override):
    config = defaultConfig.copy()
    # load config from file
    config.update(json.load(open(filename)))
    # inject override
    config.update(override)
    assert isinstance(config['workflow'], list)
    return config

def load_models(config, extract_features, all_algos):
    def create_model(config):
        model = config['model']
        params = config.copy()
        del params['model']
        if 'base' in params:
            params['base'] = baseModelMap[params['base']]
        return modelMap[model](extract_features, all_algos, **params)
    workflow = map(create_model, config['workflow'])
    # monkey patch thresholdModel
    models_patch(workflow)
    return workflow

# patch thresholdModel to ensure it has correctly linked rankingModel
def models_patch(models):
    model_refs = dict()

    for model in models:
        model_refs[model.__class__.__name__] = model

    for model in models:
        model.model_refs = model_refs
