from elasticsearch import Elasticsearch
from fuzzywuzzy import process

from parseRosetta import Task, site

from index_elasticsearch_wikipedia import INDEX_NAME, normalize, \
    load_visited, rd, index_wiki_algorithm_entry

from parseWikipedia import get_wiki_page, is_algorithm_page
from impl_languages_deduplication import get_standardized_lang

import json
from cassandra.cluster import Cluster

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

visitedwiki = load_visited()
indexedimpl = set(rd.hkeys('rosetta-mapping-success'))

cluster = Cluster(['127.0.0.1'])  # localhost
session = cluster.connect()  # default key space
session.set_keyspace('crosswikis')

FUZZY_THRESHOLD = 79

UPDATING = True

def safe_print(s):
    try:
        print s
    except UnicodeEncodeError:
        print s.encode('utf8')
    except UnicodeDecodeError:
        print s.decode('utf8')
    except Exception:
        print 'printing error'

def index_rosetta():
    category = site.Pages['Category:Programming Tasks']
    counter = 0
    for page in category:
        counter += 1
        safe_print('#%d, looking for page: %s'
            % (counter, page.page_title))
        if page.page_title not in indexedimpl or UPDATING:  # save time
            algo_ids = get_corres_wikipedia_algo_id(page)
            if algo_ids is not None:
                if len(algo_ids) > 0 and type(algo_ids[0]) == list:
                    algo_ids = [algo
                        for algo in algo_ids[0] if algo is not None]
                if len(algo_ids) > 0:
                    index_rosetta_page(page, algo_ids)

def index_rosetta_page(page, algo_ids):
    pagetask = Task(page)  # extract data from page using Task from pr

    for impl in pagetask.solutions:
        body = {
            'language': impl['language'],
            'algorithm': algo_ids,
            'source': 'rosetta',
            'implementation': impl['content'],
        }

        if len(algo_ids) > 1:
            body['description'] = '\n'.join(pagetask.task_summary)

        es.index(index=INDEX_NAME, doc_type='implementation',
            id='rosetta:' + normalize(pagetask.task_name) + ':' +
            get_standardized_lang(impl['language'].decode('utf8'), rd),
            body=body)

def get_sorted_similar_links(taskname, links):
    taskname = taskname.encode('utf8')
    choices = [link.encode('utf8') for link in links]
    try:
        res = process.extract(taskname, choices)
    except Exception as e:
        rd.sadd('rosetta-mapping-taskname-coding-error', str(e) + taskname)
        return []
    if res is not None:
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
        return id

    rd.sadd('rosetta-mapping-error-indexing-error',
        page_title + ' -> ' + linktitle)
    return None

# returns the algo id if find the algorithm already indexed,
# None otherwise
def get_id_of_corresponding_algorithm(linktitle, page_title, fuzzy=False):
    id = convert_to_id(linktitle)
    result = es.get(index=INDEX_NAME, doc_type='algorithm',
        id=id, ignore=404)
    if result['found']:
        return id

    if fuzzy:
        body = {
            "query": {
                "match": {
                    "name": {
                        "query": "merge sort",
                        "fuzziness": "auto"
                    }
                }
            }
        }
        r = es.search(index=INDEX_NAME, doc_type='algorithm',
            body=body, size=1)
        if r['hits']['total'] > 0:
            return r['hits'][0]['_id']

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

    # first, try wikilinks that has titles similar to the task name,
    # these links are sorted by confidence of fuzzy matching
    id = nel_wikilinks_fuzzy(wikilinks, page.page_title)
    if id is not None:
        return [id]

    # then use wikipedia api's auto-suggest to find corresponding
    # wikipedia page
    id = nel_title_suggest(page.page_title, False)
    if id is not None:
        return [id]

    # # then use elasticsearch fuzzy match task to indexed algorithm
    # # check if indexed
    # id = nel_title_elasticsearch(page.page_title)
    # if id is not None:
    #     return id

    # then, use crosswikis dictionary to get the most possible wiki link
    id = nel_title_crosswikis(page.page_title)
    if id is not None:
        return [id]

    # # finally, if none of the links is similar to the task name,
    # # 1, store the task description
    # # 2, relate the implementation with ALL wiki algorithms pages
    # #    mentioned in description
    # ids = nel_wikilinks_match_all(wikilinks, page.page_title)
    # if len(ids) > 0:
    #     return ids

    rd.sadd('rosetta-mapping-error-undefinable-wikilinks', page.page_title)
    print ''
    return None

def nel_wikilinks_fuzzy(wikilinks, page_title):
    if len(wikilinks) == 0:
        # no any wiki links
        rd.sadd('rosetta-mapping-error-no-wiki-links', page_title)
    else:
        # first, try wikilinks that has titles similar to the task name,
        # these links are sorted by confidence of fuzzy matching
        for link in get_sorted_similar_links(page_title, wikilinks):
            # check if indexed
            id = get_id_of_corresponding_algorithm(link, page_title)
            if id is None:
                # try to index this algorithm
                wikipage = get_wiki_page(link)
                if wikipage is not None:
                    id = index_corresponding_algorithm(wikipage, link,
                        page_title)
                safe_print(id)
            if id is not None:
                rd.hset('rosetta-mapping-success', page_title,
                    json.dumps([id]))
                rd.sadd('rosetta-mapping-similars-success', page_title)
                safe_print(id)
                print '--first'
                return [id]

def nel_title_suggest(page_title, auto_suggest=True):
    wikipage = get_wiki_page(page_title, auto_suggest)
    if wikipage is not None:
        # check if indexed
        id = get_id_of_corresponding_algorithm(page_title, page_title)
        if id is None:
            # try to index this algorithm
            id = index_corresponding_algorithm(wikipage, page_title,
                page_title)
        if id is not None:
            rd.hset('rosetta-mapping-success', page_title,
                json.dumps([id]))
            rd.sadd('rosetta-mapping-success-wikipedia-autosuggest',
                page_title)
            safe_print(id)
            print '--second'
            return [id]

def nel_title_elasticsearch(page_title):
    # TODO search on name and alt_name
    if id is not None:
        rd.hset('rosetta-mapping-success', page_title, json.dumps([id]))
        rd.sadd('rosetta-mapping-success-wikipedia-autosuggest',
            page_title)
        safe_print(id)
        print '--second'
        return [id]

def nel_title_crosswikis(page_title):
    query = "SELECT cprob, entity FROM queries WHERE anchor = %s"
    suggested_wikilinks = list(session.execute(query, [page_title]))
    suggested_wikilinks = sorted(suggested_wikilinks,
        key=lambda tup: tup[0])
    if len(suggested_wikilinks) > 0:
        # get the most confident link
        toplink = suggested_wikilinks[0][1]
        wikipage = get_wiki_page(toplink.replace('_', ' '))
        if wikipage is not None:
            # check if indexed
            id = get_id_of_corresponding_algorithm(toplink, page_title)
            if id is None:
                # try to index this algorithm
                id = index_corresponding_algorithm(wikipage, toplink,
                    page_title)
            if id is not None:
                rd.hset('rosetta-mapping-success', page_title,
                    json.dumps([id]))
                rd.sadd('rosetta-mapping-success-crosswikis',
                    page_title)
                safe_print(id)
                print '--third'
                return [id]

def nel_wikilinks_match_all(wikilinks, page_title):
    ids = list()
    for link in wikilinks:
        wikipage = get_wiki_page(link)
        if wikipage is not None and is_algorithm_page(wikipage):
            # check if indexed
            id = get_id_of_corresponding_algorithm(link, page_title)
            if id is None:
                # try to index this algorithm
                id = index_corresponding_algorithm(wikipage, link,
                    page_title)
                if id is None:
                    continue
            ids.append(id)
    if len(ids) > 0:
        rd.hset('rosetta-mapping-success', page_title,
            json.dumps(ids))
        rd.sadd('rosetta-mapping-success-all-algo-links', page_title)
        safe_print(ids)
        print '--all-link'

    return ids

def convert_to_id(title):
    return str(title.encode('utf8').lower()).replace('_', '-')

if __name__ == '__main__':
    index_rosetta()
    # page = site.Pages['Deepcopy']
    # algo_ids = get_corres_wikipedia_algo_id(page)
    # if algo_ids is not None:
    #     index_rosetta_page(page, algo_ids)
