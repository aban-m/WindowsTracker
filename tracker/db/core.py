import sqlite3
from datetime import datetime

def connect(path):
    return sqlite3.connect(
        path,
        check_same_thread = False,
        detect_types = sqlite3.PARSE_DECLTYPES
    )

def close(conn): conn.close()

def initiate_database(conn, init_script = 'schema.sql'):
    with open(init_script, 'r') as fp:
        conn.executescript(fp.read())

def prepare_window(conn, title, process):
    result = conn.execute('''
        SELECT id FROM Windows WHERE title = ? AND process = ?
    ''', (title, process)).fetchone()
    if result: return result[0]

    # create a window
    return conn.execute('''
        INSERT INTO Windows
        (title, process) VALUES
        (?, ?)
    ''', (title, process)
    ).lastrowid

def insert(conn, windows, active_index, afk, timestamp = None, commit = True):
    if timestamp is None: timestamp = datetime.now()

    active_id = prepare_window(conn, *windows[active_index]) if active_index is not None else None
    ids = [prepare_window(conn, *window) for window in windows]

    event_id = conn.execute('''
        INSERT INTO EventMetadata
        (timestamp, active_window_id, is_afk) VALUES (?, ?, ?)
    ''', (timestamp, active_id, afk)).lastrowid

    conn.executemany('''
        INSERT INTO EventData
        (event_id, window_id) VALUES (?, ?)
    ''', [(event_id, id) for id in ids])

    if commit: conn.commit()

if __name__ == '__main__':
    conn = connect('tracker.db')
