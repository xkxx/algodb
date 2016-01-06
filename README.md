# AlgoDB

Mad (╯°□°)╯'ing.

A search engine for algorithms.

<img width="1435" alt="screen shot 2015-12-17 at 3 12 00 pm" src="https://cloud.githubusercontent.com/assets/744973/11888391/ae4567f4-a4f1-11e5-88d2-4acdef598df6.png">

## Setup

1. Run the DB by following the README instructions in `elasticsearch_dumps`
2. Run the web server README in `www`

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

### google_trends
An experiment on using google trends to rank equal-score search results
