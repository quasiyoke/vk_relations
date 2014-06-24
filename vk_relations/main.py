import datetime
import models
import peewee
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
            person = models.Person.select().where(models.Person.id == person_kwargs['id']).get()
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
        print "\nchange for: %d" % before.id
        print "from: %s" % (before.relation or 'None')
        print "to:   %s" % (after_relation or 'None')
        print "partner_id from: %s" % (before_partner_id or 'None')
        print "partner_id to:   %s" % (after_partner_id or 'None')

        before.relation         = after_relation
        before.relation_partner = after_partner_id
        before.save()


@models.database.commit_on_success
def check_activity():
    now = datetime.datetime.utcnow()
    persons_counter = 0
    persons_groups_counter = 0
    
    persons_without_groups = models.Person.select().where((models.Person.groups_count == 0) | (models.Person.groups_count == None))
    for person in persons_without_groups:
        activity_details = vk.get_activity_details(person.id)
        person.set_activity_details(activity_details)
        person.activity_check_date = now
        person.save()
        persons_counter += 1
        for group_id in activity_details['groups']:
            try:
                models.PersonGroup.create(
                    person=person,
                    group=group_id,
                )
            except peewee.IntegrityError:
                models.Group.create(id=group_id)
                models.PersonGroup.create(
                    person=person,
                    group=group_id,
                )
            persons_groups_counter += 1
    
    persons_and_groups = models.PersonGroup \
                               .select(models.PersonGroup, models.Person, models.Group) \
                               .join(models.Group) \
                               .switch(models.PersonGroup) \
                               .join(models.Person) \
                               .where(models.Person.activity_check_date < now)
    for person_and_group in persons_and_groups:
        activity_details = vk.get_activity_details(person.id)
        person.set_activity_details(activity_details)
        person.activity_check_date = now
        person.save()

    print '%d persons processed' % persons_counter
    print '%.1f groups/person' % (float(persons_groups_counter) / persons_counter)
    print '%.3f sec/person' % (float((datetime.datetime.utcnow() - now).seconds) / persons_counter)
