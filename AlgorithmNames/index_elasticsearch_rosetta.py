from elasticsearch import Elasticsearch
from fuzzywuzzy import process

from parseRosetta import Task, site

from index_elasticsearch_wikipedia import INDEX_NAME, normalize, \
    load_visited, rd, index_wiki_algorithm_entry

from parseWikipedia import get_wiki_page, is_algorithm_page

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

visitedwiki = load_visited()
indexedimpl = set(rd.smembers('rosetta-mapping-success'))

FUZZY_THRESHOLD = 79

def index_rosetta():
    category = site.Pages['Category:Programming Tasks']
    for page in category:
        if page.page_title not in indexedimpl:  # save time
            print 'looking for page:', page.page_title
            res = get_corres_wikipedia_algo_id(page)
            if res is not None:
                (algo_ids, description) = res
                if algo_ids is not None:
                    index_rosetta_page(page, algo_ids, description)

def index_rosetta_page(page, algo_ids, description):
    pagetask = Task(page)  # extract data from page using Task from pr

    for impl in pagetask.solutions:
        body = {
            'language': impl['language'],
            'algorithm': algo_ids,
            'source': 'rosetta',
            'implementation': impl['content'],
            'description': description
        }

        print '----task name:', pagetask.task_name
        print '----lang:', impl['language']
        print '----algos:', algo_ids

        es.index(index=INDEX_NAME, doc_type='implementation',
            id='rosetta:' + normalize(pagetask.task_name) + ':' +
            impl['language'].decode('utf8'), body=body)

def get_sorted_similar_links(taskname, links):
    taskname = taskname.encode('utf8')
    choices = [link.encode('utf8') for link in links]
    try:
        res = process.extract(taskname, choices)
    except Exception as e:
        rd.sadd('rosetta-mapping-taskname-coding-error', str(e) + taskname)
        return []
    if res is not None:
        print 'confidence: ', res
        res = [link for (link, confidence) in res
            if confidence > FUZZY_THRESHOLD]
        return sorted(res, key=lambda x: x[1], reverse = True)
    else:
        return []

# returns the algo id when indexing succeed,
# None otherwise
def index_corresponding_algorithm(wikipage, linktitle, page_title):
    # try to index this algorithm
    if wikipage is not None:
        id = index_wiki_algorithm_entry(wikipage, linktitle,
            visitedwiki)
        rd.sadd('rosetta-mapping-success', page_title)
        return id

    rd.sadd('rosetta-mapping-error-indexing-error',
        page_title + ' -> ' + linktitle)
    return None

# returns the algo id if find the algorithm already indexed,
# None otherwise
def get_id_of_corresponding_algorithm(linktitle, page_title):
    id = convert_to_id(linktitle)
    print '--looking for id:', id
    result = es.get(index=INDEX_NAME, doc_type='algorithm',
        id=id, ignore=404)
    if result['found']:
        rd.sadd('rosetta-mapping-success', page_title)
        return id

    rd.sadd('rosetta-mapping-error-correspage-notfound',
        page_title)
    return None

# for each of the wiki links in rosetta code algorithm page,
# check if we've indexed this algorithm,
# return the id of the corresponding algorithm, None if not found
def get_corres_wikipedia_algo_id(page):
    wikilinks = [linktitle
        for (linksite, linktitle) in list(page.iwlinks())
        if linksite == 'wp']

    if len(wikilinks) == 0:
        # no any wiki links
        rd.sadd('rosetta-mapping-error-no-wiki-links', page.page_title)
        return None

    # first, try wikilinks that has titles similar to the task name,
    # these links are sorted by confidence of fuzzy matching
    for link in get_sorted_similar_links(page.page_title, wikilinks):
        # check if indexed
        id = get_id_of_corresponding_algorithm(link, page.page_title)
        if id is not None:
            rd.sadd('rosetta-mapping-similars-success', page.page_title)
            return ([id], '')
        # try to index this algorithm
        wikipage = get_wiki_page(link)
        id = index_corresponding_algorithm(wikipage, link, page.page_title)
        if id is not None:
            rd.sadd('rosetta-mapping-similars-success', page.page_title)
            return ([id], '')

    # then, if none of the links is similar to the task name,
    # 1, store the task description
    # 2, relate the implementation with ALL wiki algorithms pages
    #    mentioned in description
    ids = list()
    for link in wikilinks:
        wikipage = get_wiki_page(link)
        if wikipage is not None and is_algorithm_page(wikipage):
            # check if indexed
            id = get_id_of_corresponding_algorithm(link, page.page_title)
            if id is not None:
                ids.append(id)
                continue
            # try to index this algorithm
            wikipage = get_wiki_page(link)
            id = index_corresponding_algorithm(wikipage, link, page.page_title)
            if id is not None:
                ids.append(id)
    if len(ids) > 0:
        return (ids, page.task_summary)

    rd.sadd('rosetta-mapping-error-undefinable-wikilinks', page.page_title)
    return None

def convert_to_id(title):
    return str(title.encode('utf8').lower()).replace('_', '-')

if __name__ == '__main__':
    index_rosetta()
