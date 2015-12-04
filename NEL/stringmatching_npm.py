import json
import requests
import sys
import unicodecsv as csv

NAME = "name"
README = "readme" #"name" # "readme"
DESC = "desc" #"description" # "desc" 
def parse_single_algo(algo, response, takeMax=1):
    jdata = json.loads(response.text)
    hits = jdata["hits"]["hits"]
    res = []
    i = 0
    for h in hits:
        algo_name = h["_source"][NAME]
        algo_description = h["_source"][DESC]
        algo_readme = h["_source"][README]
        res.append((algo_name, algo_description, algo_readme))
        i += 1
        if i == takeMax:
            break
    return res  
    
def run_elastic_search(algolist, takeMax):
    mapping = {}
    url = "http://localhost:9200/throwtable/algorithm/_search" 
    for algo in algolist:
        query = json.dumps({
            "query": {
                "multi_match" : {
                    "query" : algo,
                    "fields" : [README, DESC] 
                }
            }
        })
        response = requests.get(url, data=query)
        res = parse_single_algo(algo, response, takeMax)
        if res:
            mapping[algo] = res
    return mapping

if __name__ == '__main__':
    algo_list = sys.argv[1]
    max_entries = int(sys.argv[2])    
    #print(run_elastic_search(["quicksort", "binary search", "mergesort", "depth first search"], 1))
    
    with open(algo_list, "rb") as f:
        reader = csv.reader(f)
        algo_names = [row[0].lower() for row in reader]    
    print(run_elastic_search(algo_names, max_entries))