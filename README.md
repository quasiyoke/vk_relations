# VK Relations

VK Relations is Python app to monitor people's relations at Vkontakte social network. It uses MySQL to store data.

## Installation
1. Install MySQL locally.
2. Execute the following commands at MySQL admin console:

        mysql> CREATE USER vk_relations_user@localhost IDENTIFIED BY "topsecret_db_password";
        mysql> CREATE DATABASE vk_relations_db;
        mysql> GRANT ALL ON vk_relations_db.* TO vk_relations_user@localhost;
3. Install [MySQLdb package.][1]
4. Install VK Relations package in a development mode at your home directory:

        $ pip install -e git+git://github.com/quasiyoke/vk_relations.git#egg=vk_relations
5. Configure VK Relations using file ```~/src/vk-relations/vk_relations/settings.json```. Example of settings.json file:

        {
            "DB_CONFIGURATIONS": {
                "PRIMARY": {
                    "NAME": "vk_relations_db",
                    "USER": "vk_relations_user",
                    "PASSWORD": "topsecret_db_password"
                }
            },
            "VK": {
                "LOGIN": "user@mail.com",
                "PASSWORD": "topsecret_vk_password"
            }
        }
6. Create all necessary DB tables by this command:

        $ setup.py create_tables

## DB Initialization
To monitor how people break and create new relations, we should save info about some group of people locally. VK Relations allows you to load set of some person's friends for this. You may specify desirable size of the group. If the man hasn't enough friends, friends of his friends will be loaded recursively.

To initialize DB with 9000 friends of user with ID = 1:

    $ setup.py init -u1 -c9000

## Alternative DB configurations
If you need more than one DB, you may put several DB configurations at ```DB_CONFIGURATIONS``` settings.json section next to the ```PRIMARY``` one.

To create necessary tables at ```experiment``` configuration, execute this:

    $ setup.py create_tables -dexperiment
You may use ```-d``` option with any VK Relations command.


  [1]: https://pypi.python.org/pypi/MySQL-python/
