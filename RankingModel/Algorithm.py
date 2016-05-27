from utils import decode_wiki_title, normalize

class Algorithm:
    def __init__(self, page_title, tag_line=None, description=None, categories = None):
        self.title = page_title
        self.tag_line = tag_line
        self.description = description
        self.categories = categories

    def __eq__(self, other):
        if not isinstance(other, Algorithm):
            return False
        return self.title == other.title

    def __hash__(self):
        return hash(self.title)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Algorithm:%s>" % self.title

def get_corresponding_algo(algo_name, db):
    algo = Algorithm(decode_wiki_title(algo_name))
    result = db.es.get(index="throwtable", doc_type='algorithm',
    id=normalize(algo.title), ignore=404)

    if not result['found']:
        print "ERROR: %s(%s) not found in elasticsearch db" % (algo_name, normalize(algo.title))
        algo.description = ""
        algo.tag_line = ""
        algo.categories = []
    else:
        doc = result['_source']
        algo.description = doc['description']
        algo.tag_line = doc['tag_line']
        algo.categories = doc['categories']
    return algo

all_algos = []
def get_all_mentioned_algo(db):
    """
        es: elasticsearch connection
        rd: redis connection
    """
    if len(all_algos) == 0:
        for (impl_name, algo_name) in db.rd.hscan_iter('rosettacode-label-algoname'):
            if len(algo_name):
                algo = get_corresponding_algo(algo_name, db)
                all_algos.append(algo)
    return all_algos
