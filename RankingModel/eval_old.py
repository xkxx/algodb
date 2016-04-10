from db_dependency import DB_beans
from classifier import get_trainable_data, inject_sample_experiment
from Algorithm import normalize

def escape_lucene(s):
    chars = ["\\", "+", "-", "=", "!", "(", ")", "{", "}", "[", "]", "<", ">", "^", "\"", "~", "*", "?", ":", "/"]

    for i in chars:
        s = s.replace(i, "\\" + i)
    return s

def flatten(l):
    if l is None:
        return []
    if not isinstance(l, list):
        return [l]

    res = []
    for i in l:
        ri = flatten(i)
        res.extend(ri)
    return res


db = DB_beans()

correct = 0
total = 0

tasks = get_trainable_data(db)
tasks = inject_sample_experiment(tasks)

for task in tasks:
    query = (r"_id:rosetta\:" + escape_lucene(normalize(task.title)) + "*")
    print
    print query
    result = db.es.search(index='throwtable',doc_type='implementation',q=query)

    hits = result['hits']['hits']

    prediction = None

    if len(hits) != 0:

        predictions = hits[0]['_source']['algorithm']
        predictions = flatten(predictions)
        prediction = predictions[0] if len(predictions) > 0 else None

    expected = task.label and normalize(task.label.title)

    if prediction != expected:
        print "Incorrect Match: %s" % expected
        print "Got: %s, Expected: %s" % (prediction, expected)

    else:
        print "Correct Match: %s - %s" % (task.title, expected)
        correct += 1

    total += 1

print "Accuracy: ", correct * 1.0 / total
