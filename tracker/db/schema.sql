DROP TABLE IF EXISTS Windows;
DROP TABLE IF EXISTS WindowsObservation;
DROP TABLE IF EXISTS AWObservation;
DROP TABLE IF EXISTS AFKObservation;

CREATE TABLE Windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    process TEXT NOT NULL
);

CREATE TABLE WindowsObservation (
    timestamp DATETIME PRIMARY KEY,
    window_id INTEGER NOT NULL,
    FOREIGN KEY (window_id) REFERENCES Windows(id)
);

CREATE TABLE AWObservation (
    timestamp DATETIME PRIMARY KEY,
    window_id INTEGER NOT NULL,
    FOREIGN KEY (window_id) REFERENCES Windows(id)
);

CREATE TABLE AFKObservation (
    timestamp DATETIME PRIMARY KEY,
    is_afk BOOLEAN NOT NULL
);
