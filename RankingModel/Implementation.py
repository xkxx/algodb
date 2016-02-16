from cassandra.query import SimpleStatement
from Algorithm import get_corresponding_algo

class Implementation:
    def __init__(self, page_title, categories, iwlinks, text,
            label=None, is_algo=False):
        self.title = page_title
        self.categories = categories
        self.iwlinks = iwlinks
        self.text = text
        self.label = label
        self.is_algo = is_algo

    def rank_trainable(self):
        return self.label is not None and self.is_algo

    def __str__(self):
        return self.title

def process_single_impl(row, rd):
    impl = Implementation(row.page_title, row.categories, row.iwlinks, row.text)
    # get corresponding wiki page
    algo_name = rd.hget('rosettacode-label-algoname', impl.title)
    if algo_name:
        algo_name = algo_name.strip()
        algo_name = algo_name if len(algo_name) > 0 else None
    # get if task is algo
    is_algo = rd.sismember('rosettacode-label-isalgo', impl.title)
    # record everything
    if algo_name:
        impl.label = get_corresponding_algo(algo_name)
    impl.is_algo = is_algo
    # commit
    return impl

def get_all_impls(cas, rd):
    """
        cas: cassandra session
        rd: redis connection
    """
    query = "SELECT * FROM rosettacode"
    statement = SimpleStatement(query, fetch_size=100)
    results = []
    for row in cas.execute(statement):
        results.append(process_single_impl(row, rd))
    return results
