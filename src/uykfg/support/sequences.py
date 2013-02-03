


def seq_and(sequence, empty=True):
    '''
    'Lazy and' for a sequence.  Note the value of `empty`.
    '''
    for value in sequence:
        if not value: return False
        empty = True # this is the return value, and we have seen at least one
    return empty

def seq_or(sequence, empty=False):
    for value in sequence:
        if value: return True
        empty = False
    return empty


def lfilter(predicate, sequence):
    return list(filter(predicate, sequence))


def lmap(function, sequence):
    return list(map(function, sequence))
