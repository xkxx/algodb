from fuzzywuzzy import fuzz
from simhash import Simhash
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer(min_df=1)

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

def title_tfidf(impl, algo):
    tfidf = vect.fit_transform([impl.title, algo.title])
    return 0.01 + (tfidf * tfidf.T).A[0][1]

def wikilink_fuzzy_ratio(impl, algo):
    max_score = 0.0
    for wikilink in impl.wikilinks:
        score = fuzzy.ratio(algo.title, wikilink)
        if score > max_score:
            max_score = score
    return max_score
feature_functions.append(wikilink_fuzzy_ratio)

def summary_similarity(impl, algo):
    # get first sentence as summary
    impl_sents = sent_tokenize(impl.text)
    algo_sents = sent_tokenize(algo.description)
    if (len(impl_sents) == 0) or (len(algo_sents) == 0):
        return 0.01

    # remove stop words
    impl_summary = ' '.join([word for word in impl_sents[0].split() if word not in (stopwords.words('english'))])
    algo_summary = ' '.join([word for word in algo_sents[0].split() if word not in (stopwords.words('english'))])

    # compute tfidf
    tfidf = vect.fit_transform([impl_summary, algo_summary])
    return 0.01 + (tfidf * tfidf.T).A[0][1]
feature_functions.append(summary_similarity)

def code_comments(impl, algo):
    pass

def extract_features(impl, algo):
    return [func(impl, algo) for func in feature_functions]
