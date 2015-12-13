from elasticsearch import Elasticsearch
import requests
import redis
import wikipedia as wiki
from manual_tagger import printPkgContent, getUserInput, normalize
from collections import Counter

TRUE_POSITIVE = 'True-Pos'
FALSE_POSITIVE = 'False-Pos'
TRUE_NEGATIVE = 'True-Neg'
FALSE_NEGATIVE = 'False-Neg'

def checkPkg(actual, expected, r):
    for algo in actual:
        if algo not in expected:
            print "Detected:", algo
            if getUserInput("Correct?"):
                r.sadd('%s:map' % pkgName, algo)
                return TRUE_POSITIVE
            else:
                return FALSE_POSITIVE
    # at this point, len(actual) != 0
    if len(expected) != 0:
        return FALSE_NEGATIVE
    else:
        return TRUE_NEGATIVE


def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    r = redis.StrictRedis()
    samples = r.smembers('samples')
    conditions = Counter()
    for pkgName in samples:
        print '================'
        printPkgContent()

        doc = es.get(id="npm:%s:js" % pkgName, index='throwtable', doc_type="implementation", ignore=404)
        if result['_found']:
            actual = sum(doc['_source']['algorithms'], [])
        else:
            actual = []
        expected = r.smembers("%s:map" % pkgName)

        result = checkPkg(actual, expected, r)

        redis.sadd('samples-%s' % result, pkgName)
        conditions[result] += 1

    for (k, v) in conditions.items():
        print "%s: %s" % (k, v)

    print "Precision:", 1.0 * conditions[TRUE_POSITIVE] / (conditions[TRUE_POSITIVE] + conditions[FALSE_POSITIVE])
    print "Recall:", 1.0 * conditions[TRUE_POSITIVE] / (conditions[TRUE_POSITIVE] + conditions[FALSE_NEGATIVE])

if __name__ == '__main__':
    main()
