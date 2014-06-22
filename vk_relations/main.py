import datetime
import models
import vk


@models.database.commit_on_success
def init(parent, count):
    now = datetime.datetime.utcnow()
    persons_relations_counter = 0
    persons_relation_partners_counter = 0
    retrieved_persons_ids = set()
    for person_kwargs in vk.get_persons(parent, count):
        person_kwargs['check_date'] = now
        if person_kwargs['relation'] and person_kwargs['relation'] not in vk.RELATIONS_SINGLE:
            persons_relations_counter += 1
            if person_kwargs['relation_partner']:
                persons_relation_partners_counter += 1
                # If we have no relation partner in DB, we should create stub of him to prevent constraint-related problems.
                if person_kwargs['relation_partner'] not in retrieved_persons_ids:
                    models.Person.create(
                        id=person_kwargs['relation_partner'],
                        check_date=now,
                    )
                    retrieved_persons_ids.add(person_kwargs['relation_partner'])

        # Person creation.
        if person_kwargs['id'] in retrieved_persons_ids:
            # If we already created this person as someone's relation partner, just update his stub with actual data.
            person = models.Person.select().where(models.Person.id == person_kwargs['id'])[0]
            for key, value in person_kwargs.items():
                setattr(person, key, value)
            person.save()
        else:
            person = models.Person.create(**person_kwargs)
        retrieved_persons_ids.add(person_kwargs['id'])
    print '%d persons saved' % len(retrieved_persons_ids)
    print '%.1f%% of retrieved persons have relations' % (float(persons_relations_counter) / len(retrieved_persons_ids) * 100)
    print '%.1f%% of retrieved persons specified relation partner' % (float(persons_relation_partners_counter) / len(retrieved_persons_ids) * 100)
    print '%.3f sec/person' % (float((datetime.datetime.utcnow() - now).seconds) / len(retrieved_persons_ids))


@models.database.commit_on_success
def check():
    # load persons from database
    # for each person load new data by id
    print "Start:"
    now = datetime.datetime.utcnow()
    for before, after in vk.get_changed_persons(models.Person.select().iterator()):
        before_partner_id = before.relation_partner and before.relation_partner.id

        after_partner_id  = after['relation_partner']
        after_relation    = after['relation']
        
        if after_partner_id and before_partner_id != after_partner_id:
            models.Person.ensure(after_partner_id)
        models.RelationChange.create(
                person = after['id'],
                relation_old = before.relation,
                relation_new = after_relation,
                relation_partner_old = before_partner_id,
                relation_partner_new = after_partner_id,
                check_date_old = before.check_date,
                check_date_new = now,
        )
        print "change for: %d" % before.id
        print "from: %r" % before.relation
        print "to: %r" % after_relation
        print "partner_id from: %r" % before_partner_id
        print "partner_id to: %r" % after_partner_id

        before.relation         = after_relation
        before.relation_partner = after_partner_id
        before.save()
