#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

import logging
import setuptools
import sys

logging.basicConfig()


class command(setuptools.Command):
    def initialize_options(self):
        self.database = 'PRIMARY'

    def finalize_options(self):
        pass
    
    def run(self):
        from vk_relations import settings
        settings.set_db_configuration(self.database)


class check(command):
    description = 'check persons\' relations for changes'

    user_options = [
        ('database=', 'd', 'which database configuration use'),
    ]

    def run(self):
        command.run(self)
        from vk_relations import main
        main.check()


class create_tables(command):
    description = 'create DB tables'

    user_options = [
        ('database=', 'd', 'which database configuration use'),
        ('reset', 'r', 'reset all data previously'),
    ]

    def initialize_options(self):
        command.initialize_options(self)
        self.reset = False

    def run(self):
        if self.reset:
            self.run_command('drop_tables')
        else:
            command.run(self)
        from vk_relations import models
        models.create_tables()
        print 'Tables were created successfully'


class drop_tables(command):
    description = 'drop all created DB tables'

    user_options = [
        ('database=', 'd', 'which database configuration use'),
    ]

    def run(self):
        command.run(self)
        answer = raw_input('Are you sure you want to clear all VK Relations data? (y/n): ')
        if 'y' == answer:
            from vk_relations import models
            models.drop_tables()
            print 'Tables were dropped successfully'
        elif 'n' == answer:
            quit()
        else:
            sys.exit()


class init(command):
    description = 'initialize DB with first persons'

    user_options = [
        ('database=', 'd', 'which database configuration use'),
        ('user-id=', 'u', 'first person which friends will be used for initialization'),
        ('count=', 'c', 'how much users should we retrieve'),
    ]

    def initialize_options(self):
        command.initialize_options(self)
        self.user_id = None
        self.count = None

    def finalize_options(self):
        command.finalize_options(self)
        if self.user_id is None:
            logging.getLogger(__name__).critical('"user-id" parameter wasn\'t specified.')
            sys.exit()
        if self.count is None:
            logging.getLogger(__name__).critical('"count" parameter wasn\'t specified.')
            sys.exit()
        self.count = int(self.count)

    def run(self):
        command.run(self)
        from vk_relations import main
        main.init(self.user_id, self.count)
        

setuptools.setup(
    name='vk_relations',
    version='0.0.1',
    description='Tool for VK relations exploration.',
    author='Pyotr Ermishkin, Andrey Vasnetsov',
    author_email='quasiyoke@gmail.com, vasnetsov93@gmail.com',
    url='https://github.com/quasiyoke/vk_relations',
    packages=[
        'vk_relations',
    ],
    install_requires=[
        'peewee',
        'requests',
        'vk_api',
    ],
    cmdclass={
        'check': check,
        'create_tables': create_tables,
        'drop_tables': drop_tables,
        'init': init,
    }
)
