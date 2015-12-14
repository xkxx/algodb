# please modify the path to throwtable
elasticdump \
  --input=elasticsearch_algorithm_v3.2.json \
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=elasticsearch_category_v3.2.json\
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=elasticsearch_implementation_v3.2.json \
  --output=http://localhost:9200/throwtable \
  --type=data


elasticdump \
  --input=elasticsearch_npm.json \
  --output=http://localhost:9200/throwtable \
  --type=data
