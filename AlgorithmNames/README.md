## Quickstart

The data dumps are generated in ../elasticsearch_dumps, but in case you want to run the indexing scripts, here's the instruction:

1. Open a terminal in this folder, and run redis
```
./run_redis.sh
```

2. Open another terminal in your elasticsearch folder, and run elasticsearch

3. run

```
pip install -r requirements.txt
```

4. run the script


## Scripts

### index_elasticsearch_rosetta.py

Indexes Rosetta Code's implementations into elasticsearch

### index_elasticsearch_rosetta_using_crosswikis.py

A new version of the above script, which maps Rosetta Code task names to Wikipedia algorithm names by using Crosswikis

### index_elasticsearch_wikipedia.py

Indexes the algorithms that belong to Wikipedia's category Algorithm

### parseAlgorithmia.py

Parses algorithm data from Algorithmia

### parseRosetta.py

Parses implementation data from Rosetta Code

### parseWikipedia.py

Parses algorithm data from Wikipedia


## CSV, JSON Files

### algorithmia.csv (824 algorithms)

Parsed from the algorithmia dump "algorithms.json".

Format: name | summary (in HTML) | card_line (one sentence summary) | call_count | language/version in algorithmia


### list_of_algo.txt

This is not a list of algorithm names :( but all the related terms linked from the page "list of algorithms".


### list_of_algorithms.csv (433 algorithms)

Parsed from the wikipedia page titled "list of algorithms".

Format: name | summary (plain text) | categories (it belongs to in wikipedia) | links (the title of links in the page)

TODO: parse runtime


### rosetta_task_names.csv (780 task names)

Each line is a task name in Rosetta Code.


### wiki_algo_category.json (1119 algorithms)

Each line is a json object:
	{'title': <string> the name of algorithm,
	'summary': <string> a description of the algorithm,
	'categories': <array of strings> the categories that the algorithm belongs to
	'links': <array of strings> the related terms linked from the algorithm page}

TODO: parse runtime

### rosetta_task_pages.json (780 algorithms)

Each line is a json object:
	{'task': <string> the name of the task,
	 'task_summary': <array of strings> the descriptions of the algorithm,
	 'solutions': [{
			'language': <string> the language of the solution,
			'content': [
				{'type': <string> 'description' or 'code',
				'value': <string> the text of this description or code},
				....]
			},
			....]
	}

TODO: parse related tasks

