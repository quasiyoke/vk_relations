#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

SETUP_DIR = os.path.dirname(os.path.abspath(__file__))

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
    ]
)
