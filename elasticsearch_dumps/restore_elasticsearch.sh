#! /usr/bin/env bash
# DELETE
curl -XDELETE 'http://localhost:9200/throwtable'

curl http://localhost:9200/throwtable -X PUT -d '
{
  "mappings": {
    "implementation": {
      "properties": {
        "algorithm": {
          "type": "string",
          "index": "not_analyzed"
        }
      }
    }
  }
}'

# ALGORITHM
elasticdump \
  --input=elasticsearch_algorithm_0219.json \
  --output=http://localhost:9200/throwtable \
  --type=data

# CATEGORY
#elasticdump \
#  --input=version4.3/elasticsearch_category_v4.3.json\
#  --output=http://localhost:9200/throwtable \
#  --type=data

# ROSETTA IMPLEMENTATION
elasticdump \
  --input=version4.3/elasticsearch_implementation_v4.3.json \
  --output=http://localhost:9200/throwtable \
  --type=data

# NPM IMPLEMENTATION
#elasticdump \
#  --input=elasticsearch_implementation_npm_inv_1.json \
#  --output=http://localhost:9200/throwtable \
#  --type=data
