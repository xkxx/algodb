from elasticsearch import Elasticsearch
import parseWikipedia as pw
import wikipedia as wiki
from nltk import tokenize
import redis

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
rd = redis.StrictRedis(host='localhost', port=6379, db=0)

def normalize(str):
    str = ''.join(e for e in str.lower())
    return '-'.join(str.split())

def get_tag_line(summary):
    if summary != '':
        return tokenize.sent_tokenize(summary)[0]
    return ''

def index_category_entry(page, algo_ids, subcate_ids):
    # page title -> category title
    # e.g. 'Category:abcd' -> 'abcd'
    title = page.title[9:]

    result = es.get(index='throwtable', doc_type='category',
        id=normalize(title), ignore=404)

    if not result['found']:
        body = {
            'name': title,
            'algorithms': algo_ids,
            'children': subcate_ids
        }

        # try to get category description from corresponding page
        corres_page = pw.get_wiki_page(title)
        if corres_page is None:
            # if there's no corresponding page,
            # get category description from category page itself
            corres_page = pw.get_wiki_page(page.title)
            if corres_page.summary == '':
                try:
                    corres_page = pw.get_wiki_page(corres_page.links[0])
                except KeyError:
                    # if there is no links, KeyError will be raised
                    # set corres_page to None,
                    # because empty summary will cause error
                    corres_page = None

        if corres_page is not None:
            body['tag_line'] = get_tag_line(corres_page.summary)
            body['description'] = corres_page.summary
        retval = es.index(index='throwtable', doc_type='category',
            id=normalize(title), body=body)
        return retval['_id']
    else:
        print page.title
        raise 'category already indexed'

def index_algorithm_entry(page, title):
    body = {
        'name': page.title,
        'tag_line': get_tag_line(page.summary),
        'description': page.summary,
        'categories': page.categories
        # TODO second iteration to parse related algorithm
    }

    # add alternate algo name
    if page.title != title:
        body['alt_names'] = [title]

    retval = es.index(index='throwtable', doc_type='algorithm',
        id=normalize(page.title), body=body)
    return retval['_id']

def index_page(title, depth, visited):
    print 'looking at page:', title
    # if title == 'Category:Free computer algebra systems':
    #     print '============================================ past ========'

    algo_id = -1
    cate_id = -1

    if title in visited:
        print 'visited'

        # get page id if it is visited
        # if it is visited as an algorithm
        retval = es.get(index='throwtable', doc_type='algorithm',
            id=normalize(title), ignore=404)
        if retval['found']:
            algo_id = retval['_id']
        # if it is visited as a category
        retval = es.get(index='throwtable', doc_type='category',
            id=normalize(title), ignore=404)
        if retval['found']:
            cate_id = retval['_id']
        return (algo_id, cate_id)

    if pw.is_category_title(title):                    # is category page
        if depth < pw.MAX_CATEGORY_DEPTH:
            page = wiki.categorypage(title)
            if page is None:
                print '-> category not found'
                mark_visited(title, visited)
                return (algo_id, cate_id)
            print '-> category'
            child_algo_ids = list()
            child_cate_ids = list()
            for member in page.categorymembers:
                (child_algo_id, child_cate_id) = index_page(member,
                    depth + 1, visited)
                if child_algo_id != -1:
                    child_algo_ids.append(child_algo_id)
                if child_cate_id != -1:
                    child_cate_ids.append(child_cate_id)

            if len(child_algo_ids) == 0 and len(child_cate_ids) == 0:
                # if not algorithm category, igore
                mark_visited(title, visited)
                return (-1, -1)
            # add self to category table, and update cate_id
            cate_id = index_category_entry(page,
                child_algo_ids, child_cate_ids)
    else:                                               # is member page
        page = pw.get_wiki_page(title)
        if page is None:
            print '-> member page not found'
            mark_visited(title, visited)
            return (algo_id, cate_id)
        if pw.is_algorithm_page(page):
            print '-> algorithm page'
            # add this algorithm to algorithm table
            algo_id = index_algorithm_entry(page, title)
        else:
            print '-> member page of other stuff'

    mark_visited(title, visited)
    return (algo_id, cate_id)

def mark_visited(title, visited):
    # add to redis
    rd.sadd('visited', title)
    visited.add(title)

def index_category(category):
    print 'start indexing...'

    visited = None

    # load from redis
    visited = set(rd.smembers('visited'))

    index_page(category, 0, visited)

index_category('Category:Algorithms')
