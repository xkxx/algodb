# Script:

## Install

Install redis and elastic search.

```
brew install redis
brew install elasticsearch
npm install elasticdump -g
```

## Quickstart

In another terminal, run elastic search
```
./run_elastic_search.sh
```

Restore data from json data dump (only one time to load data into db)
```
./restore_elasticsearch.sh
```

## Other scripts

Backup all the tables in elasticsearch into a json file
```
backup_elasticsearch.sh
```

# Database

`elasticsearch_category.json`
> the elasticsearch database dump for categories
> currently: ? categories

`elasticsearch_algorithm.json`
> the elasticsearch database dump for algorithms
> currently: ? algorithms

`elasticsearch_implementation.json`
> the elasticsearch database dump for implementations
> currently: ? implementations

