import os
import re

# Read algo names and get test doc corpus
algo_file_name = "../AlgorithmNames/list_of_algo.txt"
test_file_folder = "testDocs"

with open(algo_file_name, "r") as f:
    algo_names = [name.lower().split() for name in f]

corpus = []
for fname in os.listdir(test_file_folder):
    with open(os.path.join(test_file_folder, fname), "r") as f:
        corpus.append(f.read().lower())

# Simple string matching:
for doc in corpus:
    algo_counts = {}
    tokens = re.split(r'\s+', doc)
    word_counts = {}
    for t in tokens:
        if t not in word_counts:
            word_counts[t] = 0
        word_counts[t] += 1

    found_algorithms = {}
    for algo in algo_names:
        algo_in_doc = {}

        # Algo is each word in the algorithm name -> merge sort is [merge, sort]
        for algo_part in algo:
            if algo_part in word_counts:
                algo_in_doc[algo_part] = word_counts[algo_part]
        if len(algo_in_doc) == len(algo):
            # All words matched. Take the min to get instances of algorithm name
            full_name = " ".join(algo)
            found_algorithms[full_name] = min(v for k, v in algo_in_doc.items())

    # Right now, limit 1 term per text, so get max occurances.
    best = max(found_algorithms, key=found_algorithms.get)
    print(best + " with count " + str(found_algorithms[best]))