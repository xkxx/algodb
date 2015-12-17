import metrics
import json
import requests

topK = [1, 3, 5, -1] # Eval on top k entries,
EVAL_FUNC = metrics.mean_reciprocal_rank

def run_eval():
    with open("google_filtered_results.json") as fp:
        jdata = json.load(fp)

    google_results = jdata.values()
    queries = jdata.keys()
    our_results = []
    for q in queries:
        our_results.append(run_query(q))

    scores = []
    for k in topK:
        scores.append(run_eval_singleK(google_results, our_results, k))
    return scores

def run_query(query):
    url = "http://localhost:9200/throwtable/algorithm/_search"
    body = json.dumps({
      'query': {
        'multi_match': {
          'query': query,
          'fields': ['name^3', 'tag_line^1.5', 'description'],
          'fuzziness': 'AUTO'
        }
      },
      'size': 50
    })
    response = requests.get(url, data=body)
    return parse_elastic_result(response)

def parse_elastic_result(response):
    jdata = json.loads(response.text)
    hits = jdata["hits"]["hits"]
    urls = []
    for hit in hits:
        name = hit["_source"]["name"]
        url_name = name.replace(" ", "_")
        url = "https://en.wikipedia.org/wiki/" + url_name
        urls.append(url)
    return urls

def run_eval_singleK(google_results, our_results, k):
    k_google = []
    k_ours = []
    for i in range(len(google_results)):
        k_google_single = []
        k_ours_single = []

        end = k
        if k == -1:
            end = len(google_results[i])

        for j in range(min(end, len(google_results[i]))):
            k_google_single.append(google_results[i][j])

        for j in range(min(end, len(our_results[i]))):
            k_ours_single.append(our_results[i][j])

        k_google.append(k_google_single)
        k_ours.append(k_ours_single)
    return EVAL_FUNC(k_google, k_ours)

if __name__ == '__main__':
    scores = run_eval()
    for i in range(len(scores)):
       print topK[i], scores[i]
