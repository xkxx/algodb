import random

allqueries = set(line for line in open('algolist.txt'))
output = open('nel_queries.txt', 'w+')

allqueries = list(allqueries)
random.shuffle(allqueries)
for query in allqueries[:50]:
    output.write(query)
