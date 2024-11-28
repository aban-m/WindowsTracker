import sqlite3
from datetime import datetime

conn = None
def connect(path):
    global conn
    conn = sqlite3.connect(
        path,
        check_same_thread = False,
        detect_types = sqlite3.PARSE_DECLTYPES
    )
def close():
    if conn: conn.close()


def initiate_database(init_script = 'schema.sql'):
    with open(init_script, 'r') as fp:
        conn.executescript(fp.read())

def prepare_window(title, process):
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

def insert_observations(timestamp, id_list):
    conn.executemany('''
        INSERT INTO WindowsObservation
        (timestamp, window_id) VALUES
        (?, ?)
    ''', [(timestamp, ID) for ID in id_list])

def insert_aw_observation(timestamp, id):
    conn.execute('''
        INSERT INTO AWObservation
        (timestamp, window_id) VALUES
        (?, ?)
    ''', (timestamp, id))

def insert_afk_observation(timestamp, afk):
    conn.execute('''
        INSERT INTO AFKObservation
        (timestamp, is_afk) VALUES
        (?, ?)
    ''', (timestamp, afk))


def insert(windows, active_index, afk, timestamp = None):
    if timestamp is None: timestamp = datetime.now()
    active_id = prepare_window(*windows[active_index])
    ids = [prepare_window(*window) for window in windows]
    insert_observations(timestamp, ids)
    insert_aw_observation(timestamp, active_id)
    insert_afk_observation(timestamp, afk)
    conn.commit()

