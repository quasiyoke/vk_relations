import datetime
import itertools
import logging
import settings
import sys
import vk_api


# Max size of `user_ids` field is 9000 now. Maximal length of ID is 9, plus delimiter.
MAX_PERSONS_ALLOWED = 9000 / 10

SEX_CHOICES = {
    1: 'female',
    2: 'male',
}

RELATION_CHOICES = {
    1: 'single',
    2: 'in_a_relationship',
    3: 'engaged',
    4: 'married',
    5: 'its_complicated',
    6: 'actively_searching',
    7: 'in_love',
}

RELATIONS_SINGLE = set(['single', 'actively_searching'])


def split(iterator, length):
    a = None
    try:
        while True:
            a = []
            for i in xrange(length):
                a.append(iterator.next())
            yield a
    except StopIteration:
        if len(a):
            yield a


def get_changed_persons(persons):
    now = datetime.datetime.now()
    for persons_request in split(persons, MAX_PERSONS_ALLOWED):
        for before, after in itertools.izip_longest(persons_request, get_persons_by_ids([person.id for person in persons_request])):
            if not before or not after or before.id != after['id']:
                logging.getLogger(__name__).critical('Response doesn\'t match request.')
                sys.exit()

            if (before.relation != after['relation']) or \
               (not before.relation_partner and after['relation_partner']) or \
               (before.relation_partner and before.relation_partner.id != after['relation_partner']):
                yield before, after
            
            before.check_date = now
            before.save()
    

def get_persons_by_ids(ids):
    api = vk_api.VkApi(settings.VK.LOGIN, settings.VK.PASSWORD);
    ids = map(str, ids)
    persons = api.method('users.get', {
        'user_ids': ','.join(ids),
        'fields': 'sex,relation',
    })
    for person in persons:
        yield prepare_person(person)


def get_persons(parent, count):
    api = vk_api.VkApi(settings.VK.LOGIN, settings.VK.PASSWORD)
    necessary_persons_ids = [parent]
    persons_with_friends_ids = []
    persons_retrieved_ids = set()
    get_persons.count = count    
    
    def process_persons(persons):
        for person in persons:
            if person['id'] in persons_retrieved_ids:
                continue
            prepare_person(person)
            persons_with_friends_ids.append(person['id'])
            persons_retrieved_ids.add(person['id'])
            if person['relation_partner'] and person['relation_partner'] not in persons_retrieved_ids:
                necessary_persons_ids.append(person['relation_partner'])
            yield person
            get_persons.count -= 1

    while get_persons.count > 0 and len(persons_with_friends_ids) or len(necessary_persons_ids):
        # Fetch necessary persons
        persons_count = min(len(necessary_persons_ids), MAX_PERSONS_ALLOWED)
        if persons_count:
            persons_ids = map(str, necessary_persons_ids[-persons_count:])
            necessary_persons_ids = necessary_persons_ids[:-persons_count]
            persons = api.method('users.get', {
                'user_ids': ','.join(persons_ids),
                'fields': 'sex,relation',
            })
            for person in process_persons(persons):
                yield person

        # Enlarge count of persons using friends
        while get_persons.count > 0 and len(persons_with_friends_ids):
            persons = api.method('friends.get', {
                'user_id': persons_with_friends_ids.pop(0),
                'count': get_persons.count,
                'fields': 'sex,relation',
            })['items']
            for person in process_persons(persons):
                yield person


def prepare_field(d, key, choices):
    try:
        value = d[key]
    except KeyError:
        value = ''
    else:
        value = choices.get(value, '')
    d[key] = value


def prepare_person(person):
    person['id'] = int(person['id'])
    prepare_field(person, 'sex', SEX_CHOICES)
    prepare_field(person, 'relation', RELATION_CHOICES)
    try:
        relation_partner = person['relation_partner']['id']
    except KeyError:
        relation_partner = None
    person['relation_partner'] = relation_partner
    return person
