import datetime

import models
import vk


def init(parent, count):
    now = datetime.datetime.now()
    i = 0
    retrieved_persons_ids = set()
    for person_data in vk.get_persons(parent, count):
        person_kwargs = {
            'id': person_data['id'],
            'sex': person_data['sex'],
            'check_date': now,
        }
        try:
            person_kwargs['relation'] = person_data['relation']
            person_kwargs['relation_partner'] = person_data['relation_partner']['id']
        except KeyError:
            pass
        else:
            # If we have no relation partner in DB, we should create stub of him to prevent constraint-related problems.
            if person_kwargs['relation_partner'] not in retrieved_persons_ids:
                models.Person.create(
                    id=person_kwargs['relation_partner'],
                    sex='male',
                    check_date=now,
                )
                retrieved_persons_ids.add(person_kwargs['relation_partner'])

        # Person creation.
        
        # If we already created this person as someone's relation partner, just update his stub with actual data.
        if person_kwargs['id'] in retrieved_persons_ids:
            person = models.Person.select().where(models.Person.id == person_kwargs['id'])[0]
            for key, value in person_kwargs.items():
                setattr(person, key, value)
            person.save()
        else:
            person = models.Person.create(**person_kwargs)
        retrieved_persons_ids.add(person_data['id'])
        i += 1
    print '%d persons saved' % i
    print '%f sec/person' % (float((datetime.datetime.now() - now).seconds) / i)
