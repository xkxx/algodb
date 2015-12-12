algolist = []
with open("algolist_raw.txt") as fp:
    for line in fp:
        if line and line[0] == ' ':
            parts = line.split('.')
            algolist.append(parts[0].strip())

with open("algolist.txt", "w") as fp:
    for algo in algolist:
        fp.write(algo + "\n")