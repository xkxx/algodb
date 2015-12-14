from elasticsearch import Elasticsearch
import mwclient as mw
import redis
from collections import Counter
from index_elasticsearch_wikipedia import normalize

def printTaskContent(task, site):
    taskPage = site.Pages[task.decode('utf8')]
    print "Task Name:", taskPage.page_title.encode('utf8')
    print "Summary:"
    print "\n".join(taskPage.text().split('\n')[:10]).encode('utf8')

def getUserInput(prompt):
    result = raw_input(prompt)
    if result == 'y':
        return True
    if result == 'n':
        return False
    return result

TRUE_POSITIVE = 'True-Pos'
FALSE_POSITIVE = 'False-Pos'
TRUE_NEGATIVE = 'True-Neg'
FALSE_NEGATIVE = 'False-Neg'

def checkPkg(taskName, actual, expected, r):
    for algo in actual:
        if algo not in expected:
            print "Detected:", algo
            if getUserInput("Correct?"):
                r.sadd('%s:map' % taskName, algo)
            else:
                return FALSE_POSITIVE
    if len(actual) != 0:
        return TRUE_POSITIVE
    # at this point, len(actual) == 0
    if len(expected) != 0:
        return FALSE_NEGATIVE
    else:
        print "No Link Detected"
        if getUserInput("Correct?"):
            return TRUE_NEGATIVE
        else:
            return FALSE_NEGATIVE

def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    site = mw.Site('rosettacode.org', path='/mw/')
    r = redis.StrictRedis()
    samples = r.smembers('samples')
    conditions = Counter()
    counter = 0
    for taskName in samples:
        print 'task # %d ================' % counter
        counter += 1
        printTaskContent(taskName, site)

        impl_id = r.hget('rosetta-id-taskname-mapping', normalize(taskName))
        if impl_id is None:
            actual = []
        else:
            result = es.get(index='throwtable', doc_type='implementation',
                id=impl_id, ignore=404)
            if result['found']:
                actual = result['_source']['algorithm']
            else:
                actual = []
        expected = r.smembers("%s:map" % taskName)

        result = checkPkg(taskName, actual, expected, r)

        print result
        r.sadd('samples-%s' % result, taskName)
        conditions[result] += 1

    for (k, v) in conditions.items():
        print "%s: %s" % (k, v)

    print "Precision:", 1.0 * conditions[TRUE_POSITIVE] / (conditions[TRUE_POSITIVE] + conditions[FALSE_POSITIVE])
    print "Recall:", 1.0 * conditions[TRUE_POSITIVE] / (conditions[TRUE_POSITIVE] + conditions[FALSE_NEGATIVE])

if __name__ == '__main__':
    main()
