#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

import setuptools


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
    ],
    cmdclass={
        'create_tables': create_tables,
    }
)
