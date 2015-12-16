elasticdump \
  --input=elasticsearch_algorithm_v3.3_original.json \
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=elasticsearch_category_v3.3.json\
  --output=http://localhost:9200/throwtable \
  --type=data