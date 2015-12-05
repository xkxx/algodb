import unicodecsv as csv
import os
from bs4 import BeautifulSoup

# Load algorith name and summaries
algo_files = ["list_of_algorithms.csv"]
algo_paths = [os.path.join("..", "AlgorithmNames", f) for f in algo_files]

algo_names = []
algo_description = []
has_html = False
for f in algo_paths:
    with open(f, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            algo_names.append(row[0])
            text = BeautifulSoup(row[1]).get_text() if has_html else row[1]
            algo_description.append(text)
    has_html = True

with open("algolist.csv", "wb") as resfile:
    writer = csv.writer(resfile)
    for i in range(len(algo_names)):
        writer.writerow([algo_names[i], algo_description[i]])
