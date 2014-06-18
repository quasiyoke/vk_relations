import datetime

import models
import vk


def init(parent, count):
    now = datetime.datetime.now()
    i = 0
    for person_data in vk.get_persons(parent, count):
        person = models.Person(
            id=person_data['id'],
            sex=person_data['sex'],
            check_date=now,
        )
        try:
            person.relation=person_data['relation']
            person.relation_partner=person_data['relation_partner']['id']
        except KeyError:
            pass
        print person.__dict__
        person.save()
        i += 1
    print '%d persons saved' % i
    print '%f sec/person' % (float((datetime.datetime.now() - now).seconds) / i)
