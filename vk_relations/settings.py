import json
import logging
import os
import sys


DIR = os.path.dirname(os.path.abspath(__file__))


def set_db_configuration(name):
    try:
        configuration = settings['DB_CONFIGURATIONS'][name]
    except KeyError, e:
        logging.getLogger(__name__).critical('DB configuration "%s" wasn\'t found at "settings.json" file.' % name)
        sys.exit()
    global DB_NAME
    global DB_USER
    global DB_PASSWORD
    try:
        DB_NAME = configuration['NAME']
        DB_USER = configuration['USER']
        DB_PASSWORD = configuration['PASSWORD']
    except KeyError, e:
        logging.getLogger(__name__).critical('DB configuration "%s" isn\'t fully defined.' % name)
        sys.exit()


try:
    f = open(os.path.join(DIR, 'settings.json'), 'rb')
    try:
        settings = json.load(f)
    except ValueError, e:
        logging.getLogger(__name__).critical('"settings.json" file format error: %s' % e)
        sys.exit()
    finally:
        f.close()
except (OSError, IOError):
    logging.getLogger(__name__).critical('"settings.json" file reading troubles')
    sys.exit()
try:
    VK_LOGIN = settings['VK']['LOGIN']
    VK_PASSWORD = settings['VK']['PASSWORD']
except KeyError, e:
    logging.getLogger(__name__).critical('"settings.json" file doesn\'t contain required field: %s' % e)
    sys.exit()
set_db_configuration('PRIMARY')
