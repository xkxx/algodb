from inflection import humanize
from collections import Counter

PER_KW_CUTOFF = 2
TOTAL_CUTOFF = 4

def link_implementation(kws, es):
    print 'link_implementation!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    func_names = kws.get('function_name', {})
    comments = kws.get('comment', {})  # ignore
    if len(func_names) == 0:
        print 'return 1'
        return None

    results = Counter()
    for func in func_names:
        for (id, score) in search_by_func(func, es):
            if score > PER_KW_CUTOFF:
                results[id] += score

    for id in results:
        if results[id] < TOTAL_CUTOFF:
            del results[id]
    if len(results) == 0 or len(results) > 3:
        print 'return 2'
        return None

    print 'results:', results

    return results.most_common(1)[0]

def search_by_func(func, es):
    tokens = humanize(func)

    response = es.search(index='throwtable', doc_type='algorithm', body={
        "query": {
            "multi_match": {
                "query": tokens,
                "type": "best_fields",
                "fuzziness": 'AUTO',
                "fields": ['name^8', 'tag_line^1.5', 'description^0.5']
            }
        }
    })

    return [(hit['_id'], hit['_score']) for hit in response['hits']['hits']]
