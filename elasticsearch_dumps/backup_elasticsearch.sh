# please modify the path to throwtable
elasticdump \
  --input=http://localhost:9200/throwtable/algorithm \
  --output=elasticsearch_algorithm.json \
  --type=data

elasticdump \
  --input=http://localhost:9200/throwtable/category \
  --output=elasticsearch_category.json \
  --type=data

elasticdump \
  --input=http://localhost:9200/throwtable/implementation \
  --output=elasticsearch_implementation.json \
  --type=data