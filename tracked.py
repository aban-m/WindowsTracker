import time
import argparse
import json
import logging

import tracker



parser = argparse.ArgumentParser(description='Manage the tracker service.')

subparsers = parser.add_subparsers(dest='command', required=True, help='Commands for the tracker service.')

status_parser = subparsers.add_parser('observe', help='Output the current tracker status as JSON.')
start_parser = subparsers.add_parser('start', help='Start the tracker service.')

start_parser.add_argument(
    '--frequency',
    type=int,
    default=600,
    help='Frequency of checks in seconds (default: 600 seconds).',
)
start_parser.add_argument(
    '--excluded-titles',
    nargs='*',
    default=[],
    help='List of window titles to exclude (default: empty list).',
)
start_parser.add_argument(
    '--excluded-processes',
    nargs='*',
    default=[],
    help='List of process names to exclude (default: empty list).',
)
start_parser.add_argument(
    '--db',
    dest = 'db_path',
    required=True,
    help='Path to the database.',
)
start_parser.add_argument(
    '--init-db',
    action='store_true',
    help='Flag to indicate if the database should be initialized (default: False).',
)
start_parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Increase verbosity level.",
)


args = parser.parse_args()

if args.command == 'observe':
    obs = tracker.Observer()
    print(json.dumps(obs.observe()))

elif args.command == 'start':
    # First, configure logging
    level_map = {
        0: logging.WARNING,  # Default
        1: logging.INFO,     # -v
        2: logging.DEBUG,    # -vv
    }
    level = level_map.get(args.verbose, logging.DEBUG)  # Beyond -vv, stick to DEBUG

    this_logger = logging.getLogger('tracker')
    
    logger_names = ['db', 'observer', 'runner', 'tracker']
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))
    
    for name in logger_names:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if not logger.handlers:
            logger.addHandler(handler)

    
    obs = tracker.Observer(
        excluded_titles = args.excluded_titles,
        excluded_processes = args.excluded_processes
    )

    conn = None
    if args.init_db:
        open(args.db_path, 'wb').close()
        conn = tracker.connect(args.db_path)
        tracker.db.initiate_database(conn, 'tracker/db/schema.sql')
    else:
        conn = tracker.connect(args.db_path)

    runner = tracker.Runner.from_observer(args.frequency, obs, conn)
    runner.run()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            this_logger.critical('Received Ctrl-C, exiting...')
            runner.stop()
            break
        
