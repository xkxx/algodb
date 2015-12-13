from elasticsearch import Elasticsearch
import requests
import redis
import wikipedia as wiki

def normalize(str):
    str = ''.join(e for e in str.lower())
    return '-'.join(str.split())

def printPkgContent(pkgName):
    pkg = requests.get("http://localhost:5984/npm/" + pkgName).json()
    print 'Package Name: ', pkg['name']
    print 'Desc:', pkg.get('description', '[NONE]')
    print 'keywords:', pkg.get('keywords', [])
    print 'Readme:\n'
    print '\n'.join(pkg.get('readme', '[NONE]').split('\n')[:15])

def getUserInput(prompt):
    result = raw_input(prompt)
    if result == 'y':
        return True
    if result == 'n':
        return False
    return result

def queryWikipedia(concept):
    flag = concept[:1]
    autoSuggest = True
    if flag == ':':
        autoSuggest = False
        concept = concept[1:]
    page = wiki.page(concept, auto_suggest=autoSuggest)
    return page.title

def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    r = redis.StrictRedis()
    samples = r.srandmember('pkgs', 100)
    for pkgName in samples:
        r.sadd('samples', pkgName)
        continue
        print '================'
        printPkgContent(pkgName)
        result = []
        while True:
            answer = getUserInput("Article? ")
            if answer == '':
                break
            page = queryWikipedia(answer)
            answer = getUserInput("Do you mean: %s page? ")
            if answer is True:
                result.append(page)
                break
        if len(result) != 0:
            r.sadd('%s:map' % pkgName, *result)

if __name__ == '__main__':
    main()
