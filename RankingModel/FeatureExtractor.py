from fuzzywuzzy import fuzz
from simhash import Simhash
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer(min_df=1)

from throwtable.KeywordExtract.code_keyword_extractor import extract_keywords

feature_functions = list()

"""
    Features from the titles
"""

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

"""
    Features from the wikilinks
"""

def iwlinks_fuzzy_ratio(impl, algo):
    max_score = 0.0
    for wikilink in impl.iwlinks:
        score = fuzz.ratio(algo.title, wikilink)
        if score > max_score:
            max_score = score
    return max_score
feature_functions.append(iwlinks_fuzzy_ratio)

"""
    Features from the summaries
"""

def summary_similarity(impl, algo):
    # get first sentence as summary
    # assume the first sentence is at most 1000 chars long
    impl_sents = sent_tokenize(impl.summary)
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

"""
    Features from the code
"""
# impl.content = [(tag, value), ...]
# tag = 'commentary' or 'code'

# whether algo's title is a part of the comments
def code_comments(impl, algo):
    comments = []
    for (tag, value) in impl.content:
        if tag == 'code':
            comments.extend( [keyword
                for (t, keyword) in keyextract_keywords(value) if t == 'comment'] )
    return fuzz.partial_ratio('\n '.join(comments), algo.title)
feature_functions.append(code_comments)

# whether algo's title is a part of the function names
def code_funcnames(impl, algo):
    funcnames = []
    for (tag, value) in impl.content:
        if tag == 'code':
            comments.extend( [keyword
                for (t, keyword) in keyextract_keywords(value) if t == 'function_name'] )
    return fuzz.partial_ratio('\n '.join(funcnames), algo.title)
feature_functions.append(code_funcnames)

"""
    Features from the commentary arround code snippets
"""

# whether algo's title is a part of the commentary
def impl_commentary(impl, algo):
    commentaries = [value for (tag, value) in impl.content if tag == 'commentary']
    return fuzz.partial_ratio('\n '.join(commentaries), algo.title)
feature_functions.append(impl_commentary)

def extract_features(impl, algo):
    return [func(impl, algo) for func in feature_functions]
