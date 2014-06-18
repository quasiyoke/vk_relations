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
    deck = [parent]
    persons_retrieved = set()
    while len(deck):
        request_users_count = min(len(deck), MAX_PERSONS_ALLOWED)
        request_users_ids = deck[-request_users_count:]
        deck = deck[:-request_users_count]
        persons_retrieved.update(request_users_ids)
        persons = api.method('users.get', {
            'user_ids': ','.join(request_users_ids),
            'fields': 'sex,relation',
        })

        # Enlarge count of persons using friends.
        i = 0
        count -= request_users_count
        while count > 0 and i < len(request_users_ids):
            response = api.method('friends.get', {
                'user_id': request_users_ids[i],
                'count': count,
                'fields': 'sex,relation',
            })['items']
            i += 1
            count -= len(response)
            persons_retrieved.update([int(person['id']) for person in response])
            persons.extend(response)

        for person in persons:
            if 'relation_partner' in person:
                # Always check out relation.
                id = str(person['relation_partner']['id'])
                if id not in persons_retrieved:
                    deck.append(id)
            count -= 1
            yield prepare_person(person)


def prepare_field(d, key, choices):
    try:
        value = d[key]
    except KeyError:
        pass
    else:
        try:
            value = choices[value]
        except KeyError:
            del d[key]
        else:
            d[key] = value


def prepare_person(person):
    prepare_field(person, 'sex', SEX_CHOICES)
    prepare_field(person, 'relation', RELATION_CHOICES)
    return person
