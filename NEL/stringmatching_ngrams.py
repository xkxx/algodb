import os
import re
import unicodecsv as csv
from nltk import ngrams
import math


def remove_stopwords(tokens, stop_words):
    return [word for word in tokens if word not in stop_words]


def load_data(algo_file_name, test_file_folder, stopword_file):
    with open(stopword_file, "r") as f:
        stop_words = set(x.strip() for x in f)

    with open(algo_file_name, "rb") as f:
        reader = csv.reader(f)
        algo_names = [tuple(row[0].lower().split()) for row in reader]
        algo_names = set(remove_stopwords(algo_names, stop_words))

    corpus = []
    file_names = []
    for fname in os.listdir(test_file_folder):
        file_names.append(fname)
        with open(os.path.join(test_file_folder, fname), "r") as f:
            corpus.append(f.read().lower())

    return stop_words, algo_names, corpus, file_names


# N-gram string matching
def string_match(stop_words, algo_names, corpus,  file_names):
    idx = 0
    maxN = max(len(name) for name in algo_names)

    detected = {}
    algo_total_frequency = {}
    for doc in corpus:
        tokens = re.split(r'\s+', doc)
        tokens = remove_stopwords(tokens, stop_words)

        algo_doc_frequency = {}
        for n in range(1, maxN+1):
            for ngram in ngrams(tokens, n):
                if ngram in algo_names:
                    name = " ".join(ngram)
                    if name not in algo_doc_frequency:
                        algo_doc_frequency[name] = 0
                    algo_doc_frequency[name] += 1
        
        for name, freq in algo_doc_frequency.items():
            if name not in algo_total_frequency:
                algo_total_frequency[name] = 0
            algo_total_frequency[name] += 1
        detected[file_names[idx]] = algo_doc_frequency
        idx += 1
    tf_idf(detected, algo_total_frequency)
    return detected


def tf_idf(doc_freq, total_freq):
    for doc, algos_found in doc_freq.items():
        for algo, freq in algos_found.items():
            doc_freq[doc][algo] = freq * math.log(1.0 * len(doc_freq) / total_freq[algo])

def run():
    # Read algo names and get test doc corpus
    algo_file_name = "algolist.csv"
    test_file_folder = "testDocs"
    stopword_file = "stopwords.txt"

    stop_words, algo_names, corpus, file_names = load_data(algo_file_name, test_file_folder, stopword_file)
    detected_algos = string_match(stop_words, algo_names, corpus,  file_names)
    for doc, algos_found in detected_algos.items():
        print("expected: " + doc, "got: " + str(algos_found))

run()