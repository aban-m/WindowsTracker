## Windows Tracker
This script watches the opeend windows periodically, saving the results in a database.
Currently, it does not do any data analysis/visualization on the result, and is only compatible with Windows.

### Usage
First, install the requirements:
```bash
pip install -r requirements.txt
```

The CLI tool `tracked.py` can be used in one of two ways.
- `./tracked observe` gives the result that would be written into the database in JSON format (allowing it to be used in a different context).
- `./tracked start` starts tracker. Usage:
```
  --frequency FREQUENCY
                        Frequency of checks in seconds (default: 600 seconds).
  --excluded-titles [EXCLUDED_TITLES ...]
                        List of window titles to exclude (default: empty list).
  --excluded-processes [EXCLUDED_PROCESSES ...]
                        List of process names to exclude (default: empty list).
  --db DB_PATH          Path to the database.
  --init-db             Flag to indicate if the database should be initialized (default: False).
  -v, --verbose         Increase verbosity level.
```

### Details
The list of opened windows are obtained using the Win32 API. Some postprocesssing is done to remove spurious processes/windows. AFK is detected by taking a screenshot of the screen as well as the mouse position, and comparing with the next result.
