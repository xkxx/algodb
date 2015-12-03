import pycurl
import urllib
from StringIO import StringIO
import json

def parse_single_algo_json(jdata, takeMax=1):
    hits = jdata["hits"]["hits"]
    res = []
    i = 0
    for h in hits:
        algo_name = h["_source"]["name"]
        algo_description = h["_source"]["description"]
        res.append((algo_name, algo_description))
        i += 1
        if i == takeMax:
            break
    return res

def parse_single_algo(algo, curl, buf):
    curl.perform()
    jdata = json.loads(buf.getvalue())
    return parse_single_algo_json(jdata)  
    
def run_elastic_search(algolist):
    curl = pycurl.Curl()
    algolist = ["quicksort", "binary search"]
    mapping = {}
    for algo in algolist:
        buf = StringIO()
        query = {"q" : algo}
        encoded = urllib.urlencode(query)
        url = "http://localhost:9200/throwtable/algorithm/_search/?" + encoded
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEDATA, buf)
        res = parse_single_algo(algo, curl, buf)
        if res:
            mapping[algo] = res
    curl.close()
    return mapping

run_elastic_search(None)