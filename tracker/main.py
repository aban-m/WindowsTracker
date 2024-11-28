import argparse
from configparser import ConfigParser

from . import utils, observer
from . import db

def make_runner(observer, frequency, conn):
    def write_callback(observer):
        status = observer.observe()
        db.insert(conn, status['windows'], status['active_index'],
                  status['afk'], timestamp = None, commit = True
        )
    runner = utils.Runner(frequency, write_callback, observer)
    return runner

