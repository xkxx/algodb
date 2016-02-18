from fuzzywuzzy import fuzz
from simhash import Simhash

feature_functions = list()

def title_fuzzy_ratio(impl, algo):
    return fuzz.ratio(impl.title, algo.title)
feature_functions.append(title_fuzzy_ratio)

def title_fuzzy_partial_ratio(impl, algo):
    return fuzz.partial_ratio(impl.title, algo.title)
feature_functions.append(title_fuzzy_partial_ratio)

def title_fuzzy_simhash(impl, algo):
    return Simhash(impl.title).distance(Simhash(algo.title))
feature_functions.append(title_fuzzy_simhash)

def wikilink_fuzzy_ratio(impl, algo):
    score = 0
    for wikilink in impl.wikilinks:
        score += fuzzy.ratio(algo.title, wikilink)
    return score
feature_functions.append(wikilink_fuzzy_ratio)

def 

def extract_features(impl, algo):
    return [func(impl, algo) for func in feature_functions]
