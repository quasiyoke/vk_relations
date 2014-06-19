import datetime

import models
import vk


def init(parent, count):
    now = datetime.datetime.now()
    i = 0
    for person_data in vk.get_persons(parent, count):
        person_kwargs = {
            'id': person_data['id'],
            'sex': person_data['sex'],
            'check_date': now
        }
        try:
            person_kwargs['relation']=person_data['relation']
            person_kwargs['relation_partner']=person_data['relation_partner']['id']
        except KeyError:
            pass
        person = models.Person.create(**person_kwargs)
        i += 1
    print '%d persons saved' % i
    print '%f sec/person' % (float((datetime.datetime.now() - now).seconds) / i)
