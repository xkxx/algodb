from elasticsearch import Elasticsearch
import requests
import redis
import wikipedia as wiki
from manual_tagger import printPkgContent, getUserInput, normalize
from collections import Counter
from index_pkg import get_links, get_npm_pkg

TRUE_POSITIVE = 'True-Pos'
FALSE_POSITIVE = 'False-Pos'
TRUE_NEGATIVE = 'True-Neg'
FALSE_NEGATIVE = 'False-Neg'

def checkPkg(pkgName, actual, expected, r, es):
    for algo in actual:
        if algo not in expected:
            print "Detected:", algo
            if getUserInput("Correct?"):
                r.sadd('%s:map' % pkgName, algo)
                return TRUE_POSITIVE
            else:
                return FALSE_POSITIVE
    if len(actual) != 0:
        return TRUE_POSITIVE
    elif len(expected) != 0:
        return FALSE_NEGATIVE
    else:
        print "No Link Detected"
        pkg = get_npm_pkg(pkgName)
        hints = get_links(pkg, es)
        print "NEL Hints:"
        for hint in hints[:15]:
            print '\t', hint
        print '\n'
        if getUserInput("Correct?"):
            return TRUE_NEGATIVE
        else:
            return FALSE_NEGATIVE

def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    r = redis.StrictRedis()
    samples = r.smembers('samples')
    conditions = Counter()
    for pkgName in samples:
        print '================'
        printPkgContent(pkgName)

        doc = es.get(id="npm:%s:js" % pkgName, index='throwtable', doc_type="implementation", ignore=404)
        if doc['found']:
            actual = sum(doc['_source']['algorithm'], [])
        else:
            actual = []
        expected = r.smembers("%s:map" % pkgName)

        result = checkPkg(pkgName, actual, expected, r, es)

        r.sadd('samples-%s' % result, pkgName)
        conditions[result] += 1

    for (k, v) in conditions.items():
        print "%s: %s" % (k, v)

    print "Precision:", 1.0 * conditions[TRUE_POSITIVE] / (conditions[TRUE_POSITIVE] + conditions[FALSE_POSITIVE])
    print "Recall:", 1.0 * conditions[TRUE_POSITIVE] / (conditions[TRUE_POSITIVE] + conditions[FALSE_NEGATIVE])

if __name__ == '__main__':
    main()
