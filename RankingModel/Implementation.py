from cassandra.query import SimpleStatement
from Algorithm import get_corresponding_algo

class Implementation:
    def __init__(self, page_title, categories, iwlinks, summary,
            label=None, is_algo=False):
        self.title = page_title
        self.categories = categories
        if iwlinks is None:
            iwlinks = set()
        self.iwlinks = iwlinks
        self.summary = summary
        # FIXME hard-coded impl content
        self.lang = 'python'
        self.content = None
        self.label = label
        self.is_algo = is_algo

    def rank_trainable(self):
        return self.label is not None and self.is_algo

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Implementation:%s>" % self.title

def process_single_impl(row, content, db):
    # print row.page_title, row.iwlinks
    impl = Implementation(row.page_title, row.categories, row.iwlinks, row.summary)
    impl.content = content
    # get corresponding wiki page
    algo_name = db.rd.hget('rosettacode-label-algoname', impl.title)
    if algo_name:
        algo_name = algo_name.strip()
        algo_name = algo_name if len(algo_name) > 0 else None
    # get if task is algo
    is_algo = db.rd.sismember('rosettacode-label-isalgo', impl.title)
    # get corresponding algo obj
    # NB: since we only train on algo, we only get algo obj if impl is algo
    if algo_name and is_algo:
        impl.label = get_corresponding_algo(algo_name, db)
    impl.is_algo = is_algo
    # commit
    return impl

def get_all_tasks(db):
    """
        Gets all rosettacode impls in dev set which has a label
    """
    tasknames = db.rd.smembers('rosettacode-label-devset')
    results = []
    for taskname in tasknames:
        # get python impl
        query = "SELECT * FROM impls WHERE page_title = %s AND lang = %s"
        statement = SimpleStatement(query, fetch_size=100)
        impl = []
        arow = None  # optimization: a single row of python impl
        for row in db.cs_rs_impl.execute(statement, [taskname, 'Python']):
            arow = row
            impl.append((row.type, row.content))

        if arow is None:
            # no python impl: get something we can use
            print "No python impl for ", taskname
            query = "SELECT * FROM impls WHERE page_title = %s LIMIT 1"
            statement = SimpleStatement(query)
            desp = list(db.cs_rs_impl.execute(statement, [taskname]))
            if len(desp) != 1:
                print taskname, desp
                print "Task not found in cassandra db"
                continue
            arow = desp[0]

        results.append(process_single_impl(arow, impl, db))

    return results
