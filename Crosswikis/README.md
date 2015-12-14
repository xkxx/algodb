# Cassandra Schema

Keyspace: crosswikis
Tables: queries, altnames

## queries

Columns
- anchor: query
- cprob: confidence level
- entity: the corresponding wikipedia page

## altnames

Inverted index of queries

Columns

- entity: wikipedia page
- cprob: confidence level
- anchor: the corresponding queries

# Files

## index_ardb_crosswikis.py

Indexing crosswikis dictionary into Ardb.
Failed because it's unstable.

## index_cassandra_crosswikis.py

Indexing crosswikis dictionary into Cassandra.

## smallset

Small example set of crosswikis dictionary.

# git ignored files

## dictionary

The crosswikis dictionary. Can be download at http://www-nlp.stanford.edu/pubs/crosswikis-data.tar.bz2/dictionary.bz2

# Commands

## Line counting

```
sed -n '$=' dictionary
```
output = 297073139

## Split dictionary

e.g. You want to split dictionary into 8 files. 297073139 / 8 = 37134142.375.

```
split -l 37134143 dictionary
```


