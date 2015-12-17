Code for evaluation:

Source of algorithm list:
http://www.scriptol.com/programming/list-algorithms.php


Files: 
  * algolist_raw.txt: Raw text file of algorithm list website. 
  * algolist.txt: List of algortihms parsed from raw file. 
  * google_search_results: Google search results for each query in algolist in JSON format. 
  * google_filtered_results.json: Final list of algorithms -> [URL] for evaluation.

Code:
  * create_algo_list.py: go from algolist_raw -> algolist
  * get_google_results.py: create google search results
  * google_parser.py: Parse JSON google search results to JSON file containing query -> [URL]
  * metrics.py: Four different type of metrics that could be used for evaluation [Spearman distance, DCG, MAP, MRR]]
  * run_final_eval.py: Runs the evaluation on the end to end system using metric in EVAL_FUNC

Usage:  
python create_algo_list.py  
Add key + start into get_google_results.py  
python get_google_results.py  
python google_parser.py [Note slow, because queries wikipedia to filter out URLs]  
python run_final_eval.py


