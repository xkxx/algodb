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

term = Terminal()
