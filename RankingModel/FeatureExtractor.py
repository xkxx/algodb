# utility
from collections import namedtuple

# extraction helper
from fuzzywuzzy import fuzz
from simhash import Simhash
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from algodb.KeywordExtract.code_keyword_extractor import extract_keywords
from algodb.AlgorithmNames.parseWikipedia import get_wiki_page
from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer(min_df=1)


"""
    Support Functions
"""

Feature = namedtuple("Feature", ['name', 'version', 'extractor'])
# feature_functions = [Feature]
feature_functions = list()

def feature(version):
    """
        feature() is a function decorator

        Usage:

        @feature(1)
        def some_feature_function(impl, algo):
            return 0.42

    """
    def feature_decorator(extractor):
        feature_functions.append(Feature(
            name=extractor.__name__,
            version=version,
            extractor=extractor))
        return extractor
    return feature_decorator

def get_cache_key(feature, impl, algo):
    return ("%s:%s" % (str(impl), str(algo)),
            "%s@%d" % (feature.name, feature.version))

def cache_get_feature(db, feature, impl, algo):
    cache = db.feature_cache
    (hkey, hfield) = get_cache_key(feature, impl, algo)
    if not cache.hexists(hkey, hfield):
        cache.hset(hkey, hfield, str(feature.extractor(db, impl, algo)))
    return float(cache.hget(hkey, hfield))

def extract_features_factory(db):
    def extract_features(impl, algo, limit_features=None,
                         feature_name_prefix=""):
        features = (limit_features if limit_features is not None else
                [f.name for f in feature_functions])  # all
        return {
            (feature_name_prefix + feat.name):
                cache_get_feature(db, feat, impl, algo)
            for feat in feature_functions
            if feat.name in features}
    return extract_features

"""
    Features from the titles

    Note: function names must be unique as they are used as cache keys.
    Whenever changes are made, make sure the version num is updated
"""

@feature(1)
def title_fuzzy_ratio(db, impl, algo):
    return fuzz.ratio(impl.title, algo.title)

@feature(1)
def title_fuzzy_partial_ratio(db, impl, algo):
    return fuzz.partial_ratio(impl.title, algo.title)

@feature(1)
def title_fuzzy_simhash(db, impl, algo):
    return Simhash(impl.title).distance(Simhash(algo.title))

@feature(1)
def title_tfidf(db, impl, algo):
    tfidf = vect.fit_transform([impl.title, algo.title])
    return (tfidf * tfidf.T).A[0][1]

"""
    Features from the wikilinks
"""

@feature(1)
def iwlinks_fuzzy_ratio(db, impl, algo):
    max_score = 0.0
    for wikilink in impl.iwlinks:
        score = fuzz.ratio(algo.title, wikilink)
        if score > max_score:
            max_score = score
    return max_score

"""
    Features from the summaries
"""

@feature(1)
def summary_similarity(db, impl, algo):
    # get first sentence as summary
    # assume the first sentence is at most 1000 chars long
    impl_sents = sent_tokenize(impl.summary)
    algo_sents = sent_tokenize(algo.description[:1000])
    if (len(impl_sents) == 0) or (len(algo_sents) == 0):
        return 0

    # remove stop words
    impl_summary = ' '.join([word for word in word_tokenize(impl_sents[0])
        if word not in (stopwords.words('english'))])
    algo_summary = ' '.join([word for word in word_tokenize(algo_sents[0])
        if word not in (stopwords.words('english'))])

    # compute tfidf
    tfidf = vect.fit_transform([impl_summary, algo_summary])
    return (tfidf * tfidf.T).A[0][1]

"""
    Features from the code
"""
# impl.content = [(tag, value), ...]
# tag = 'commentary' or 'code'

# whether algo's title is a part of the comments
@feature(1)
def code_comments(db, impl, algo):
    comments = []
    for (tag, value) in impl.content:
        if tag == 'code':
            comments.extend( [keyword
                for (t, keyword) in extract_keywords(value) if t == 'comment'] )
    return fuzz.partial_ratio('\n '.join(comments), algo.title)

# whether algo's title is a part of the function names
@feature(1)
def code_funcnames(db, impl, algo):
    funcnames = []
    for (tag, value) in impl.content:
        if tag == 'code':
            funcnames.extend( [keyword
                for (t, keyword) in extract_keywords(value) if t == 'function_name'] )
    return fuzz.partial_ratio('\n '.join(funcnames), algo.title)

"""
    Features from the commentary arround code snippets
"""

# whether algo's title is a part of the commentary
@feature(1)
def impl_commentary(db, impl, algo):
    commentaries = [value for (tag, value) in impl.content if tag == 'commentary']
    return fuzz.partial_ratio('\n '.join(commentaries), algo.title)

"""
    Features from Wikipedia auto-suggest
"""

def _get_auto_suggest(db, impl):
    if not db.rd.hexists('rosettacode-title-auto-suggest', impl.title):
        suggested = get_wiki_page(impl.title)
        title = suggested.title if suggested is not None else 'None'
        db.rd.hset('rosettacode-title-auto-suggest', impl.title, title)
    return db.rd.hget('rosettacode-title-auto-suggest', impl.title)

# whether Wikipedia auto-suggest thinks this is a matching page
@feature(2)
def wikipedia_auto_suggest(db, impl, algo):
    suggested_title = _get_auto_suggest(db, impl)
    return fuzz.ratio(suggested_title, algo.title)

"""
    Features of algorithm/non-algorithm
"""

# whether Wikipedia auto-suggest finds a wikipedia link for the implementation
@feature(4)
def wikipedia_auto_suggest_has_link(db, impl, algo):
    suggested_title = _get_auto_suggest(db, impl)
    return int(suggested_title != 'None')

@feature(1)
def title_has_algorithm(db, impl, algo):
    return int('algorithm' in impl.title.lower())

@feature(1)
def description_has_algorithm(db, impl, algo):
    return int('algorithm' in impl.summary.lower())

@feature(1)
def wikipage_category_algorithm_check(db, impl, algo):
    '''
        used for threshold model,
        algo must be the top candidate
    '''
    for category in algo.categories:
        if 'algorithm' in category.lower():
            return 1
    return 0

@feature(1)
def wikipage_category_math_check(db, impl, algo):
    '''
        used for threshold model,
        algo must be the top candidate
    '''
    for category in algo.categories:
        if 'math' in category.lower():
            return 1
    return 0

@feature(1)
def wikipage_content_algorithm_check(db, impl, algo):
    '''
        used for threshold model,
        algo must be the top candidate
    '''
    return int('algorithm' in algo.description)
