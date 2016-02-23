from db_dependency import DB_beans
from classifier import get_trainable_data
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

FP = 0
FN = 0
TP = 0
TN = 0
for (task, label) in get_trainable_data(db):
    query = (r"_id:rosetta\:" + escape_lucene(normalize(task.title)) + "*")
    print 
    print query
    result = db.es.search(index='throwtable',doc_type='implementation',q=query)

    hits = result['hits']['hits']

    if len(hits) == 0:
        FN += 1
        continue

    predictions = hits[0]['_source']['algorithm']
    predictions = flatten(predictions)
    prediction = predictions[0] if len(predictions) > 0 else None

    if prediction is None:
        FN += 1
        continue

    expected = normalize(label.title)

    if prediction != expected:
        print "Incorrect Match: %s" % expected
        print "Got: %s, Expected: %s" % (prediction, expected)
        FN += 1

    else:
        print "Correct Match: %s - %s" % (task.title, expected)
        TP += 1

print "TP:", TP
print "FN:", FN
print "Precision:", 1.0 * TP / (TP + FN)
