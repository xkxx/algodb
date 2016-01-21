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

def parse_prior(expected):
    expectedCorrect = []
    expectedWrong = []
    for e in expected:
        if e.startswith('!!'):
            expectedWrong.append(e[2:])
        else:
            expectedCorrect.append(e)
    return (expectedCorrect, expectedWrong)

def checkPkg(pkgName, expected, r, es):
    (expectedCorrect, expectedWrong) = parse_prior(expected)
    # try link pkg
    pkg = get_npm_pkg(pkgName)
    hints = get_links(pkg, es)
    print '================'
    printPkgContent(pkgName)
    actual = hints[:1]
    for algo in actual:
        if algo in expectedWrong:
            return FALSE_POSITIVE
        # if algo in expectedCorrect, continue
        if algo not in expectedCorrect:
            print "Detected:", algo
            if getUserInput("Correct?"):
                r.sadd('%s:map' % pkgName, algo)
                return TRUE_POSITIVE
            else:
                r.sadd("%s:map" % pkgName, '!!%s' % algo)
                return FALSE_POSITIVE
    if len(actual) != 0:
        return TRUE_POSITIVE
    elif len(expectedCorrect) != 0: # can be linked, but not
        return FALSE_NEGATIVE
    else:
        print "NEL Hints:"
        for hint in hints[:15]:
            print '\t', hint
        print '\n'
        print "No Link Detected"
        if getUserInput("Correct?"):
            return TRUE_NEGATIVE
        else:
            r.sadd('%s:map' % pkgName, '~~EXISTS~~')
            return FALSE_NEGATIVE

def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    r = redis.StrictRedis()
    samples = r.smembers('samples')
    conditions = Counter()
    for pkgName in samples:
        expected = r.smembers("%s:map" % pkgName)
        result = checkPkg(pkgName, expected, r, es)
        print result

        r.sadd('samples-%s' % result, pkgName)
        conditions[result] += 1

    for (k, v) in conditions.items():
        print "%s: %s" % (k, v)

    print "Precision:", 1.0 * conditions[TRUE_POSITIVE] / (conditions[TRUE_POSITIVE] + conditions[FALSE_POSITIVE])
    print "Recall:", 1.0 * conditions[TRUE_POSITIVE] / (conditions[TRUE_POSITIVE] + conditions[FALSE_NEGATIVE])

if __name__ == '__main__':
    main()
