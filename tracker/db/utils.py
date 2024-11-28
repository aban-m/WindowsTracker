from os.path import isfile
from sqlite3 import connect

def is_tracker_db(path):
    if not isfile(path): return False
    with open(path, 'rb') as fp:
        header = fp.read(16)
        if header != b'SQLite format 3\x00': return False
    # now likely a sqlite3 file
    try:
        connect(path).close()
    except Exception as e:
        return False

    # TODO: Actually check the schema.
    return True
