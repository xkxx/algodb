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

Explanation of the NEL strategies that each versions use, the bugs fixed, or the new features.

## version 1

Exact string match

## version 2.0

Fuzzy string match

Match all algo link in description (for debugging purpose)

## version 2.1

Fixed rosetta code commentary parsing bug

## version 3.0

Fuzzy string match wikipedia link titles

Crosswikis

Match all algo link in description (for debugging purpose)

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

Wikipedia api auto-suggest given the task name

Crosswikis

Match all algo link in description

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

Wikipedia auto-suggest (with lower fuzziness, works better!)

Crosswikis

## Other scripts

Backup all the tables in elasticsearch into a json file
```
backup_elasticsearch.sh
```


