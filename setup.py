#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

import logging
import setuptools
import sys

logging.basicConfig()


class create_tables(setuptools.Command):
    description = 'create DB tables'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from vk_relations import models
        models.create_tables()


class init(setuptools.Command):
    description = 'initialize DB with first persons'

    user_options = [
        ('user-id=', 'u', 'first person which friends will be used for initialization'),
        ('count=', 'c', 'how much users should we retrieve'),
    ]

    def initialize_options(self):
        self.user_id = None
        self.count = None

    def finalize_options(self):
        if self.user_id is None:
            logging.getLogger(__name__).critical('"user-id" parameter wasn\'t specified.')
            sys.exit()
        if self.count is None:
            logging.getLogger(__name__).critical('"count" parameter wasn\'t specified.')
            sys.exit()
        self.count = int(self.count)

    def run(self):
        from vk_relations import main
        main.init(self.user_id, self.count)
        

setuptools.setup(
    name='vk_relations',
    version='0.0.1',
    description='Tool for VK relations exploration.',
    author='Pyotr Ermishkin',
    author_email='quasiyoke@gmail.com',
    url='https://github.com/quasiyoke/vk_relations',
    packages=[
        'vk_relations',
    ],
    install_requires=[
        'MySQLdb',
        'peewee',
        'requests',
        'vk_api',
    ],
    cmdclass={
        'create_tables': create_tables,
        'init': init,
    }
)
