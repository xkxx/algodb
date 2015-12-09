# throwtable

Mad (╯°□°)╯'ing.

## Setup

1. Run the DB by following the instructions in `elasticsearch_dumps`
2. Run the web server in `www`

## Parts

### AlgorithmNames
Parses algorithm names from Algorithmia data and Wikipedia's "List of Algorithm" page and "Algorithm" category
Parses implementations from Rosetta Code

### Crosswikis
Parses data from Crosswikis, mapping from queries to wikipedia page with confidence level

### elasticsearch_dumps
Contains Elasticsearch dumps for algortithms, categories and implementations, and scripts for backup and restore database

### lang-pkgs
Parses data from npm

### github
Parses data from a GitHub README

### NEL
Finds algortihm names in plain text

### www
The website search engine of the database.

