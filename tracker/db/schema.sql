DROP TABLE IF EXISTS Windows;
DROP TABLE IF EXISTS EventMetadata;
DROP TABLE IF EXISTS EventData;


CREATE TABLE Windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    process TEXT NOT NULL
);

CREATE TABLE EventMetadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    active_window_id INTEGER,
    is_afk BOOLEAN DEFAULT False,
    FOREIGN KEY (active_window_id) REFERENCES Windows(id)
);

CREATE TABLE EventData (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    window_id INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES EventMetadata(id),
    FOREIGN KEY (window_id) REFERENCES Windows(id)
);