# please modify the path to throwtable
elasticdump \
  --input=http://localhost:9200/throwtable/algorithm \
  --output=elasticsearch_algorithm_v4.0.json \
  --type=data

elasticdump \
  --input=http://localhost:9200/throwtable/category \
  --output=elasticsearch_category_v4.0.json \
  --type=data

elasticdump \
  --input=http://localhost:9200/throwtable/implementation \
  --output=elasticsearch_implementation_v4.0.json \
  --type=data