# please modify the path to throwtable
elasticdump \
  --input=version3.3/elasticsearch_algorithm_v3.3.json \
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=version3.3/elasticsearch_category_v3.3.json\
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=version3.3/elasticsearch_implementation_v3.3.json \
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=elasticsearch_npm.json \
  --output=http://localhost:9200/throwtable \
  --type=data
