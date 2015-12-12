# please modify the path to throwtable
elasticdump \
  --input=elasticsearch_algorithm.json \
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=elasticsearch_category.json\
  --output=http://localhost:9200/throwtable \
  --type=data

elasticdump \
  --input=elasticsearch_implementation.json \
  --output=http://localhost:9200/throwtable \
  --type=data


elasticdump \
  --input=elasticsearch_npm.json \
  --output=http://localhost:9200/throwtable \
  --type=data
