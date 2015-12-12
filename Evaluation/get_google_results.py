import requests
import json
import os

result_dir = 'google_search_results'
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

algolist = []
with open('algolist.txt', 'r') as fp:
    for line in fp:
        algolist.append(line.strip())

start = XXX # MAKE SURE TO CHANGE
key = XXX # MAKE SURE TO CHANGE
search_id = '016575028638610389147%3A5wbwpqg1878'
url = 'https://www.googleapis.com/customsearch/v1?q='

for i in range(start, min(start+100, len(algolist))):
    algo = algolist[i]
    algo = algo.replace('/', ' ')
    rq = url + algo + '&cx=' + search_id + '&key=' + key
    r = requests.get(rq)
    json_str = r.content
    json_data = json.loads(json_str)
    with open(os.path.join(result_dir, algo) + '.json', 'w') as jfp:
        json.dump(json_data, jfp, indent=4)
