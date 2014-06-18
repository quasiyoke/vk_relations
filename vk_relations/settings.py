import json
import logging
import sys

logging.basicConfig()


class Struct:
    def __init__(self, d):
        self.__dict__.update(d)


try:
    f = open('settings.json', 'rb')
    settings = json.load(f)
    f.close()
except (OSError, IOError):
    logging.getLogger(__name__).critical('"settings.json" file reading troubles')
    sys.exit()
for key, value in settings.items():
    if isinstance(value, dict):
        value = Struct(value)
    globals()[key] = value
