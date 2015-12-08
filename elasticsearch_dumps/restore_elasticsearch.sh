# please modify the path to throwtable
elasticdump \
  --input=elasticsearch_algorithm.json, elasticsearch_category.json, elasticsearch_implementation.json \
  --output=http://localhost:9200/throwtable \
  --type=data
