from urllib import unquote
from blessings import Terminal
from sklearn.tree import export_graphviz

def normalize(str):
    str = ''.join(e for e in str.lower())
    return '-'.join(str.split())

def decode_wiki_title(wiki_title):
    unquoted = unquote(wiki_title)
    title = unquoted.replace('_', ' ')
    return title

def is_positive(impl):
    return impl.label is not None and impl.is_algo

def export_tree(clf):
    export_graphviz(clf, out_file='tree.dot')

def init_f1_metrics():
    return {
        'true-positive': [0],
        'false-positive': [0],
        'true-negative': [0],
        'false-negative': [0]
    }

def print_f1(metrics):
    precision = 1.0 * metrics['true-positive'][0] / (metrics['true-positive'][0] +
        metrics['false-positive'][0])
    recall = 1.0 * metrics['true-positive'][0] / (metrics['true-positive'][0] +
        metrics['false-negative'][0])
    print '   Precision :\t', precision
    print '   Recall :\t', recall
    print '   F1: ', 2 * (precision * recall) / (precision + recall)

term = Terminal()
