import redis

rd = redis.StrictRedis(host='localhost', port=16379, db=0)

f = open('dictionary')

def parseRawCrosswikisRow(row):
    """Parses the fields from a row in dictionary.

    Args:
    row: A row from dictionary as a string.

    Returns: A tuple of the form (anchor, cprob, entity, info).
    """
    tabParts = row.split('\t')
    anchor = tabParts[0]
    middleParts = tabParts[1].split(' ')
    cprob = middleParts[0]
    entity = middleParts[1]
    info = ' '.join(middleParts[2:])
    return (anchor, cprob, entity, info)

def printExample():
    try:
        smallset = open('smallset')
        for line in smallset:
            (anchor, cprob, entity, info) = parseRawCrosswikisRow(line)
            print '===================================================='
            print 'anchor', anchor
            print 'cprob', cprob
            print 'entity', entity
            print 'raw=', line
    except Exception:
        print 'you forget to generate smallset'

def index_redis_crosswikis():
    out = open('out', 'w+')
    for line in f:
        (anchor, cprob, entity, _) = parseRawCrosswikisRow(line)
        try:
            anchor = anchor.decode('utf8').strip()
            anchor = anchor.replace('\"', '')
            anchor = anchor.strip()
            rd.zadd(anchor, num(cprob), entity)
            print anchor
            out.write('anchor: %s, cprob: %0.2f, entity: %s'
                % (anchor.encode('utf8'), num(cprob), entity.encode('utf8')))
        except UnicodeDecodeError:
            pass

def num(s):
    try:
        return float(s)
    except Exception:
        print 'converting error:', s

index_redis_crosswikis()
