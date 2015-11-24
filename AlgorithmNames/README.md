CSV, JSON Files:
================

1. algorithmia.csv (824 algorithms)
------------------------------------

	Parsed from the algorithmia dump "algorithms.json".

	Format: name | summary (in HTML) | card_line (one sentence summary) | call_count | language/version in algorithmia


2. list_of_algo.txt
--------------------

	This is not a list of algorithm names :( but all the related terms linked from the page "list of algorithms". 


3. list_of_algorithms.csv (433 algorithms)
------------------------------------------

	Parsed from the wikipedia page titled "list of algorithms".

	Format: name | summary (plain text) | categories (it belongs to in wikipedia) | links (the title of links in the page)

	TODO: parse runtime
	

4. rosetta_task_names.csv (780 task names)
-------------------------------------------

	Each line is a task name in Rosetta Code. 


5. wiki_algo_category.json (1119 algorithms)
---------------------------------------------

	Each line is a json object:
		{'title': <string> the name of algorithm,
		'summary': <string> a description of the algorithm,
		'categories': <array of strings> the categories that the algorithm belongs to
		'links': <array of strings> the related terms linked from the algorithm page}

	TODO: parse runtime


6. rosetta_task_pages.json (780 algorithms)
---------------------------------------------

	Each line is a json object:
		{'task': <string> the name of the task,
		 'task_summary': <array of strings> the descriptions of the algorithm,
		 'solutions': [{
				'language': <string> the language of the solution,
				'content': [{'type': <string> 'description' or 'code',
					     'value': <string> the text of this description or code},
					    ....]
			      },
			      ....
			      ]
		}

	TODO: parse related tasks

Script:
=======

1. rundbservers.sh
--------------------

	runs the redis and elasticsearch server.
	elasticsearch is for algorithms, categories, and implementations,
	redis is for visited terms when indexing wikipedia.

2. backup_elasticsearch.sh
---------------------------

	backup all the tables in elasticsearch into a json file

3. restore_elasticsearch.sh
----------------------------

	restore elasticsearch db from the json file

Database:
=========

1. dump.rdb
------------

	the redis database dump

2. elasticsearch_wikipedia.json
-------------------------------

	the elasticsearch database dump
	for now: 110 categories + 1028 algorithms

