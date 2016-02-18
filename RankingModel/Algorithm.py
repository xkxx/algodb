from urllib import unquote

class Algorithm:
    def __init__(self, page_title, description):
        self.title = page_title
        self.description = description

    def __eq__(self, other):
        if not isinstance(other, Algorithm):
            return False
        return self.title == other.title

    def __hash__(self):
        return hash(self.title)

    def __str__(self):
        return self.title

def decode_wiki_title(wiki_title):
    unquoted = unquote(wiki_title)
    title = unquoted.replace('_', ' ')
    return title

def get_corresponding_algo(algo_name, description):
    return Algorithm(decode_wiki_title(algo_name), description)

def get_all_mentioned_algo(es, rd):
    """
        es: elasticsearch connection
        rd: redis connection
    """
    all_algos = []
    for (impl_name, algo_name) in rd.hscan_iter('rosettacode-label-algoname'):
        if len(algo_name):
            description = 
            algo = get_corresponding_algo(algo_name, description)
            all_algos.append(algo)
    return all_algos
