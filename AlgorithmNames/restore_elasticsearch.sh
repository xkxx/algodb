# please modify the path to throwtable
elasticdump \
  --input=elasticsearch_wikipedia.json \
  --output=http://localhost:9200/throwtable \
  --type=data
