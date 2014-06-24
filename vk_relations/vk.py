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


def get_activity_details(id):
    activity_details = {
        'birth_date': None,
        'friends_count': None,
        'groups': [],
        'posts_count': None,
    }
    api = vk_api.VkApi(settings.VK_LOGIN, settings.VK_PASSWORD)

    # `birth_date`, `friends_count` fetching
    try:
        person_data = api.method('users.get', {
            'user_ids': id,
            'fields': 'birthdate,counters'
        })[0]
    except vk_api.vk_api.ApiError, e:
        if 15 == e.code:
            # User was deactivated, so he has no friends, groups and posts.
            return activity_details
        else:
            logging.getLogger(__name__).critical(e)
            sys.exit()
    try:
        activity_details['birth_date'] = datetime.datetime.strptime(person_data['bdate'], '%d.%m.%Y')
    except (KeyError, ValueError): # Nothing to do if there's no birth_date or only day and month specified.
        pass
    try:
        activity_details['friends_count'] = person_data['counters']['friends']
    except KeyError:
        # Another type of deactivated users.
        return activity_details

    # `groups` fetching
    try:
        groups_count = person_data['counters']['groups']
    except KeyError:
        groups_count = 0
    if groups_count:
        MAX_GROUPS_COUNT = 1000
        for offset in xrange(0, person_data['counters']['groups'], MAX_GROUPS_COUNT):
            try:
                groups = api.method('groups.get', {
                    'user_id': id,
                    'offset': offset,
                })['items']
            except vk_api.vk_api.ApiError:
                if 260 == e.code:
                    # Access to the groups list is denied due to the user's privacy settings.
                    break
                else:
                    logging.getLogger(__name__).critical(e)
                    sys.exit()
            activity_details['groups'].extend(groups)

    # `posts_count` fetching
    MAX_POSTS_COUNT = 100
    try:
        posts = api.method('wall.get', {
            'owner_id': id,
            'count': MAX_POSTS_COUNT,
        })['items']
    except vk_api.vk_api.ApiError:
        logging.getLogger(__name__).critical(e)
        sys.exit()
    else:
        if len(posts):
            activity_details['posts_count'] = float(len(posts)) / (datetime.datetime.now() - datetime.datetime.fromtimestamp(posts[-1]['date'])).total_seconds() * 24 * 3600
    
    return activity_details

def get_changed_persons(persons):
    now = datetime.datetime.utcnow()
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
    api = vk_api.VkApi(settings.VK_LOGIN, settings.VK_PASSWORD);
    ids = map(str, ids)
    persons = api.method('users.get', {
        'user_ids': ','.join(ids),
        'fields': 'sex,relation',
    })
    for person in persons:
        yield prepare_person(person)


def get_persons(parent, count):
    api = vk_api.VkApi(settings.VK_LOGIN, settings.VK_PASSWORD)
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
            if person['relation_partner'] and person['relation_partner'] not in persons_retrieved_ids:
                necessary_persons_ids.append(person['relation_partner'])
            yield person
            get_persons.count -= 1

    while get_persons.count > 0 and len(persons_with_friends_ids) or len(necessary_persons_ids):
        # Fetch necessary persons
        persons_count = min(len(necessary_persons_ids), MAX_PERSONS_ALLOWED)
        if persons_count:
            persons_ids = necessary_persons_ids[-persons_count:]
            necessary_persons_ids = necessary_persons_ids[:-persons_count]
            for person in process_persons(get_persons_by_ids(persons_ids)):
                yield person

        # Enlarge count of persons using friends
        while get_persons.count > 0 and len(persons_with_friends_ids):
            try:
                persons = api.method('friends.get', {
                    'user_id': persons_with_friends_ids.pop(0),
                    'count': get_persons.count,
                    'fields': 'sex,relation',
                })['items']
            except vk_api.vk_api.ApiError, e:
                if 15 == e.code:
                    # User was deactivated, so he has no friends.
                    continue
                else:
                    logging.getLogger(__name__).critical(e)
                    sys.exit()
            for person in process_persons(itertools.imap(prepare_person, persons)):
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
