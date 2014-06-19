# VK relations

VK relations is Python app to monitor people's relations at Vkontakte social network. It uses MySQL to store data.

## Installation
1. Install MySQL locally.
2. Execute the following commands at MySQL admin console:

        mysql> CREATE USER vk_relations_user@localhost IDENTIFIED BY "topsecret_mysql_password";
        mysql> CREATE DATABASE vk_relations_db;
        mysql> GRANT ALL ON vk_relations_db.* TO vk_relations_user@localhost;
3. Install [MySQLdb package.][1]
4. Install VK relations package in a development mode at your home directory:

        $ pip install -e git+git://github.com/quasiyoke/vk_relations.git#egg=vk_relations
5. Configure VK relations using file ```~/vk_relations/vk_relations/settings.json```. Example of settings.json file:

		{
			"DB": {
				"NAME": "vk_relations_db",
				"USER": "vk_relations_user",
				"PASSWORD": "topsecret_mysql_password"
			},
			"VK": {
				"LOGIN": "user@mail.com",
				"PASSWORD": "topsecret_vk_password"
            }
		}
6. Create all necessary DB tables by this command:

        $ setup.py create_tables

  [1]: https://pypi.python.org/pypi/MySQL-python/
