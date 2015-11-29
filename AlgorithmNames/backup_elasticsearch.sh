# please modify the path to throwtable
elasticdump \
  --input=http://localhost:9200/throwtable \
  --output=elasticsearch_wikipedia.json \
  --type=data
