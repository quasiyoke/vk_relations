import json
import logging
import os
import sys


DIR = os.path.dirname(os.path.abspath(__file__))


class Struct:
    def __init__(self, d):
        self.__dict__.update(d)


try:
    f = open(os.path.join(DIR, 'settings.json'), 'rb')
    try:
        settings = json.load(f)
    except ValueError, e:
        logging.getLogger(__name__).critical('"settings.json" file format error: ' + unicode(e))
        sys.exit()
    finally:
        f.close()
except (OSError, IOError):
    logging.getLogger(__name__).critical('"settings.json" file reading troubles')
    sys.exit()
for key, value in settings.items():
    if isinstance(value, dict):
        value = Struct(value)
    globals()[key] = value
