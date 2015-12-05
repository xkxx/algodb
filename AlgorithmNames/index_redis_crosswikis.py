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

for line in f:
    (anchor, cprob, entity, info) = parseRawCrosswikisRow(line)
    print '===================================================='
    print anchor, cprob, entity, info
    print 'raw=', line
