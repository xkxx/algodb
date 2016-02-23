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

def iwlink_fuzzy_ratio(impl, algo):
    score = 0
    for iwlink in impl.iwlinks:
        score += fuzz.ratio(algo.title, iwlink)
    return score
feature_functions.append(iwlink_fuzzy_ratio)

def summary_similarity(impl, algo):
    # get first sentence as summary
    # assume the first sentence is at most 1000 chars long
    impl_sents = sent_tokenize(impl.text[:1000])
    algo_sents = sent_tokenize(algo.description[:1000])
    if (len(impl_sents) == 0) or (len(algo_sents) == 0):
        return 0.01

    # remove stop words
    impl_summary = ' '.join([word for word in word_tokenize(impl_sents[0])
        if word not in (stopwords.words('english'))])
    algo_summary = ' '.join([word for word in word_tokenize(algo_sents[0])
        if word not in (stopwords.words('english'))])

    # compute tfidf
    tfidf = vect.fit_transform([impl_summary, algo_summary])
    return 0.01 + (tfidf * tfidf.T).A[0][1]
feature_functions.append(summary_similarity)

def code_comments(impl, algo):
    pass

def extract_features(impl, algo):
    return [func(impl, algo) for func in feature_functions]
