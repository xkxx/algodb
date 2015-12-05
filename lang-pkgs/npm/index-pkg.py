from elasticsearch import Elasticsearch
import sys
sys.path.append('../../NEL')

import stringmatch
import json
import time
import math
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

dump = open('results.json')

def get_text_content(pkg):
  return [(pkg['desc'], 2.0)
          (pkg['readme'], 1.0)
         ]

def match_valid(algo, score, weight):
  if score > 1.0:
    return True

def get_es_id(pkg):
  return 'npm:%s:js' % pkg['name']

def compute_pkg_weight(pkg):
  return pkg['downloads'] * 1.0 / math.log(int(time.time() * 1000) - pkg['timeUpdated'])

def add_to_db(pkg, impls):
  es.index(index=INDEX_NAME,
    doc_type='implementation',
    id=get_es_id(pkg),
    body={
      'language': 'js',
      'algorithm': [impls],
      'source': 'npm',
      'description': pkg['desc'],
      'instruction': {
         'package': pkg['name']
         'command': 'npm install ' + pkg['name']
         'content': pkg['readme']
      },
      'popularity': compute_pkg_weight(pkg)

  })

def main():
  for line in dump:
    pkg = json.loads(line)
    texts = get_text_content(pkg)
    impls = []
    for (text, weight) in texts:
      result = stringmatch.stringmatch(text)
      for (algo, score) in result:
        if match_valid(algo, score, weight):
          impls.append(algo)
    if len(impls) > 0:
      add_to_db(pkg, impls)
