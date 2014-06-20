import logging
import settings
import vk_api

logging.basicConfig()

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


def get_persons(parent, count):
    MAX_PERSONS_ALLOWED = 1000
    api = vk_api.VkApi(settings.VK.LOGIN, settings.VK.PASSWORD)
    necessary_persons_ids = [parent]
    persons_with_friends_ids = []
    persons_retrieved_ids = set()
    get_persons.count = count

    def process_persons(persons):
        for person in persons:
            if person['id'] in persons_retrieved_ids:
                continue
            persons_with_friends_ids.append(person['id'])
            persons_retrieved_ids.add(person['id'])
            try:
                partner_id = str(person['relation_partner']['id'])
            except KeyError:
                pass
            else:
                if partner_id not in persons_retrieved_ids:
                    necessary_persons_ids.append(partner_id)
            yield prepare_person(person)
            get_persons.count -= 1
    
    while get_persons.count > 0 and len(persons_with_friends_ids) or len(necessary_persons_ids):
        # Fetch necessary persons
        persons_count = min(len(necessary_persons_ids), MAX_PERSONS_ALLOWED)
        if persons_count:
            persons_ids = necessary_persons_ids[-persons_count:]
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
    prepare_field(person, 'sex', SEX_CHOICES)
    prepare_field(person, 'relation', RELATION_CHOICES)
    return person
