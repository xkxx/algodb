# please modify the path to throwtable
elasticdump \
  --input=../lang-pkgs/npm/results.json \
  --output=http://localhost:9200/throwtable \
  --type=data
