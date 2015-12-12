from cassandra.cluster import Cluster
import sys

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

def index_cassandra_crosswikis(filename):
    cluster = Cluster()  # localhost
    session = cluster.connect()  # default key space
    session.set_keyspace('crosswikis')

    f = open(filename)
    out = open(filename + '.out', 'w+')
    for line in f:
        (anchor, cprob, entity, _) = parseRawCrosswikisRow(line)
        try:
            anchor = anchor.decode('utf8').strip()
            anchor = anchor.replace('\"', '')
            anchor = anchor.strip()
            if len(anchor) > 0:
                session.execute("INSERT INTO queries (anchor, cprob, entity) VALUES (%s, %s, %s)", [anchor.encode('utf8').decode('utf8'), num(cprob), entity.encode('utf8').decode('utf8')])
                print anchor
                out.write('anchor: %s, cprob: %0.2f, entity: %s'
                    % (anchor.encode('utf8'), num(cprob),
                    entity.encode('utf8')))
        except UnicodeDecodeError:
            pass

def num(s):
    try:
        return float(s)
    except Exception:
        return 0.0
        print 'converting error:', s

if __name__ == '__main__':
    index_cassandra_crosswikis(sys.argv[1])
