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


# Database

## version 1

Exact string match

## version 2.0

Fuzzy string match wikipedia link titles, then match all algo link in description

## version 2.1

Fixed rosetta code commentary parsing bug

## version 3.0

Fuzzy string match wikipedia link titles, then crosswikis, then match all algo link in description

Fixed rosetta code language parsing bug

## version 3.1

Adjusted fuzziness

## version 3.2

Fixed another rosetta code language parsing bug

Deduplication of programming language of all implementations

## version 3.3

Used crosswikis as a source for Algorithms' associated queries

## version 4.0

Fuzzy string match wikipedia link titles

then use wikipedia api auto-suggest given the task name

then use crosswikis

then match all algo link in description

(all linkings must link to wikipedia page detected to be algorithm)

## version 4.1

Strategies are the same as v4.0, but since algorithm page detection has
a significant number of false negatives, now linkings are not checked for
whether it is an algorithm page.

## version 4.2

Fuzzy string match

Wikipedia auto-suggest

## version 4.3

Fuzzy string match

Wikipedia auto-suggest (with lower fuzziness)

Crosswikis

## Other scripts

Backup all the tables in elasticsearch into a json file
```
backup_elasticsearch.sh
```


