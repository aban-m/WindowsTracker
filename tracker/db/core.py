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

def insert_observations(conn, timestamp, id_list):
    conn.executemany('''
        INSERT INTO WindowsObservation
        (timestamp, window_id) VALUES
        (?, ?)
    ''', [(timestamp, ID) for ID in id_list])

def insert_aw_observation(conn, timestamp, id):
    conn.execute('''
        INSERT INTO AWObservation
        (timestamp, window_id) VALUES
        (?, ?)
    ''', (timestamp, id))

def insert_afk_observation(conn, timestamp, afk):
    conn.execute('''
        INSERT INTO AFKObservation
        (timestamp, is_afk) VALUES
        (?, ?)
    ''', (timestamp, afk))


def insert(conn, windows, active_index, afk, timestamp = None, commit = True):
    if timestamp is None: timestamp = datetime.now()
    active_id = prepare_window(conn, *windows[active_index])
    ids = [prepare_window(conn, *window) for window in windows]
    insert_observations(conn, timestamp, ids)
    insert_aw_observation(conn, timestamp, active_id)
    insert_afk_observation(conn, timestamp, afk)
    if commit: conn.commit()

