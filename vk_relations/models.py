import peewee

import settings


database = peewee.MySQLDatabase(settings.DB.NAME, settings.DB.USER, settings.DB.PASSWORD)

RELATION_TYPE_CHOICES = (
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
    sex = peewee.CharField(choices=SEX_CHOICES)
    relation = peewee.ForeignKeyField('self', related_name='relates_with', null=True)
    relation_type = peewee.CharField(choices=RELATION_TYPE_CHOICES)
    check_date = peewee.DateTimeField()

    class Meta:
        database = database
        indexes = (
            (('sex, relation_type'), False),
            (('relation_type'), False),
        )

class RelationChange(peewee.Model):
    person = peewee.ForeignKeyField(Person, related_name='relation_changes')
    relation_old = peewee.ForeignKeyField(Person, related_name='+', null=True)
    relation_new = peewee.ForeignKeyField(Person, related_name='+', null=True)
    relation_type_old = peewee.CharField(choices=RELATION_TYPE_CHOICES)
    relation_type_new = peewee.CharField(choices=RELATION_TYPE_CHOICES)
    check_date_old = peewee.DateTimeField()
    check_date_new = peewee.DateTimeField()

    class Meta:
        database = database
        indexes = (
            (('check_date_old', 'check_date_new'), False),
            (('check_date_new'), False),
        )
