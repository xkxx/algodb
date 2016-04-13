from urllib import unquote

def normalize(str):
    str = ''.join(e for e in str.lower())
    return '-'.join(str.split())

def decode_wiki_title(wiki_title):
    unquoted = unquote(wiki_title)
    title = unquoted.replace('_', ' ')
    return title
