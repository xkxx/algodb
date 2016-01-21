npm Linker and Indexer
======================

Dependencies
------------

Most scripts here require a running Elasticesearch instance with algorithm
dump loaded. You should also have the following PyPI packages installed:

* `elasticsearch` (for db)
* `requests` (for npm testing)
* `dateutil` (for date parsing)
* `python-rake` (for keyword extraction)
* `mistune` (for markdown parsing)

`eval_verify.py` and single-pkg linking test also requires that you have
couchdb running with a replica of the npm database loaded under dbname `npm`.
Check https://github.com/npm/npm-registry-couchapp for details.

The evaluation scripts additionally require redis to be installed and running.

Indexing
--------

Before you run the linker, make sure you have downloaded `results.json` via
`git lfs` (487MB)

Note: Keyword Extraction is slow! May take ~6hrs.

### Keyword Extraction

```bash
> python2 index_pkg.py
```

### Keyword Extraction w/ Crosswikis

Note: make sure you have the cleaned Crosswikis! check
run `python2 elasticsearch-dump/clean-cw.py` if you haven't already.

```bash
> python2 index_pkg_cw.py
```

### Reverse Matching

```bash
> python2 index_pkg_all.py
> python2 link-top-results.py
```

Evaluation
----------

Before doing any of the following, make sure you have generated a test set.
To generate a test set usable for evaluating precision, do:

```bash
> python2 manual_tagger.py 1
```

to generate a test set usable for evaluating recall, do:

```bash
> python2 manual_tagger.py 0
```

### Offline Evaluation

Offline evaluation allows you to evaluate without having to have indexed all
of npm first (kw extraction variants only)

```bash
> python2 eval_verify.py
```

### Online Evaluation

Online Evaluation evaluates against implementations in the running
elasticsearch instance.

```bash
> python2 eval_verify_online.py
```

Dataset Dumps
-------------

### list.json

A JSON file containing a list of all npm packages, retrieved on Nov 12.

### results.json

A JSON-line file containing package data on each npm package and number of
downloads during the month of Oct 12 - Nov 12. Retrieved on Nov 12.
