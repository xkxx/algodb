curl -XDELETE 'http://localhost:9200/throwtable'

elasticdump \
  --input=version4.3/elasticsearch_algorithm_v4.3.json \
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=version4.3/elasticsearch_category_v4.3.json\
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=version4.3/elasticsearch_implementation_v4.3.json \
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=elasticsearch_implementation_npm_inv_1.json \
  --output=http://localhost:9200/throwtable \
  --type=data
