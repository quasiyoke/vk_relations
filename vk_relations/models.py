import datetime
import logging
import peewee
import settings
import sys
import vk


database = peewee.MySQLDatabase(settings.DB_NAME, user=settings.DB_USER, passwd=settings.DB_PASSWORD)
try:
    database.connect()
except peewee.DatabaseError, e:
    logging.getLogger(__name__).critical('Can\'t connect to DB: %s' % e)
    sys.exit()
    

RELATION_CHOICES = (
    ('single', 'Single'),
    ('in_a_relationship', 'In a relationship'),
    ('engaged', 'Engaged'),
    ('married', 'Married'),
    ('in_love', 'In love'),
    ('its_complicated', 'It\'s complicated'),
    ('actively_searching', 'Actively searching'),
)


class Person(peewee.Model):
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    id = peewee.IntegerField(primary_key=True)
    sex = peewee.CharField(choices=SEX_CHOICES, default='')
    relation = peewee.CharField(choices=RELATION_CHOICES, default='')
    relation_partner = peewee.ForeignKeyField('self', related_name='relates_with', null=True)
    check_date = peewee.DateTimeField()

    class Meta:
        database = database

    @staticmethod
    def ensure(id):
        '''
        If there's no user with such ID in DB, creates it.
        '''
        try:
            Person.select().where(Person.id == id)[0]
        except IndexError:
            person_kwargs = vk.get_persons_by_ids([id]).next()
            person_kwargs['check_date'] = datetime.datetime.now()
            if person_kwargs['relation_partner']:
                Person.ensure(person_kwargs['relation_partner'])
            Person.create(**person_kwargs)
        

class RelationChange(peewee.Model):
    person = peewee.ForeignKeyField(Person, related_name='relation_changes')
    relation_old = peewee.CharField(choices=RELATION_CHOICES, default='')
    relation_new = peewee.CharField(choices=RELATION_CHOICES, default='')
    relation_partner_old = peewee.ForeignKeyField(Person, related_name='relation_partners_old', null=True)
    relation_partner_new = peewee.ForeignKeyField(Person, related_name='relation_partners_new', null=True)
    check_date_old = peewee.DateTimeField()
    check_date_new = peewee.DateTimeField()

    class Meta:
        database = database
        indexes = (
            (('check_date_old', 'check_date_new'), False),
        )


def create_tables():
    try:
        Person.create_table()
        RelationChange.create_table()
    except peewee.DatabaseError, e:
        logging.getLogger(__name__).critical(e)
        sys.exit()


def drop_tables():
    try:
        RelationChange.drop_table()
    except peewee.DatabaseError, e:
        e = unicode(e)
        if not e.startswith('(1051'): # Unknown table
            logging.getLogger(__name__).critical(e)
            sys.exit()
    try:
        Person.drop_table()
    except peewee.DatabaseError, e:
        e = unicode(e)
        if not e.startswith('(1051'): # Unknown table
            logging.getLogger(__name__).critical(e)
            sys.exit()
