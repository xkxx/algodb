Simple string matching linking:

Reads document corpus from testDocs and reads list of algorithm names from ../AlgorithmNames/list_of_algo.txt. For each document, finds the number of times each algorithm name appeared and prints out the most frequent name per document.


Ngram string matching:

Uses similar model as string matching, but instead finds words by filtering stop words and then using n gram matching.


Elastic Search string matching:
For every algorithm, uses elastic search to search the algortihm in the npm document focus and returns the top values
usage:
python string_matching_npm.py algolist.csv topK_from_elastic_search
