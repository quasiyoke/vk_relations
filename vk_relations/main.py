import datetime

import models
import vk


def init(parent, count):
    now = datetime.datetime.now()
    persons_relations_counter = 0
    persons_relation_partners_counter = 0
    retrieved_persons_ids = set()
    for person_data in vk.get_persons(parent, count):
        person_kwargs = {
            'id': person_data['id'],
            'check_date': now,
        }
        try:
            person_kwargs['sex'] = person_data['sex']
        except KeyError:
            pass
        try:
            person_kwargs['relation'] = person_data['relation']
            persons_relations_counter += 1
            person_kwargs['relation_partner'] = person_data['relation_partner']['id']
            persons_relation_partners_counter += 1
        except KeyError:
            pass
        else:
            # If we have no relation partner in DB, we should create stub of him to prevent constraint-related problems.
            if person_kwargs['relation_partner'] not in retrieved_persons_ids:
                models.Person.create(
                    id=person_kwargs['relation_partner'],
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
    print '%d persons saved' % len(retrieved_persons_ids)
    print '%.1f%% of retrieved persons have relations' % (float(persons_relations_counter) / len(retrieved_persons_ids) * 100)
    print '%.1f%% of retrieved persons specified relation partner' % (float(persons_relation_partners_counter) / len(retrieved_persons_ids) * 100)
    print '%.3f sec/person' % (float((datetime.datetime.now() - now).seconds) / len(retrieved_persons_ids))

def check():
    # load persons from database
    # for each person load new data by id
    print "Start:"
    ids = [];
    before = [];
    after  = [];
    for person in models.Person.select():
        before += [person];
        ids += [str(person.id)];
    for person in vk.get_persons_relations(ids):
        after  += [person];
    
    # List order is implied
    if( len(before) != len(after)):
        print "List size missmatch!";
        print str(len(before)) + " & " + str(len(after));
        exit();

    for i in range(0, len(before)-1):

        after_partner_id  = 0;
        after_relation    = "";
        before_partner_id = before[i].relation_partner

        after_partner_id  = after[i].get('relation_partner',{"id":None})['id']
        after_relation    = after[i].get("relation","")

        if before[i].id == after[i]['id']:
            if (before[i].relation != after_relation) or (before_partner_id != after_partner_id):
                print "change for: " + str(before[i].id);
                print "from: " + repr(str(before[i].relation));
                print "to: " + repr(str(after_relation));
                print "partner_id from: " + str(before_partner_id);
                print "partner_id to: "   + str(after_partner_id);

check();