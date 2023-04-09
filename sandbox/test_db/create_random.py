import random
from django.utils.timezone import datetime, make_aware
from decimal import Decimal as D
import uuid
from datetime import timedelta
from string import ascii_letters


def create_random_length(min_length, max_length):
    choices = range(min_length, max_length)
    return choices[random.randint(0, len(choices) - 1)]


def create_random_boolean():
    return random.randint(0, 1)


def create_random_binary(length=50):
    for _ in range(length):
        return bytes([create_random_boolean() for _ in range(length)])


def create_random_char(length=10):
    return ''.join((random.choice(ascii_letters) for _ in range(0, length)))


def create_random_slug(length=10):
    return create_random_char(length=length)


def create_random_text(min_length=0, max_length=100):
    length = random.randint(min_length, max_length)
    return create_random_char(length=length)


def create_random_datetime(timestamp_min=datetime(1986, 11, 9).timestamp(),
                           timestamp_max=datetime(2025, 11, 9).timestamp()):
    result = None
    while result is None:
        try:
            '''
            result = datetime(
                year=randint(1986, 2025),
                month=randint(1, 12),
                day=randint(1, 31),
                hour=randint(0, 23),
                minute=randint(0, 30),
                second=randint(0, 59),
                microsecond=randint(0, 999),
            )
            '''
            random_timestamp = random.uniform(timestamp_min, timestamp_max)
            result = datetime.fromtimestamp(random_timestamp)
            result = make_aware(result)
        except ValueError:
            continue
    return result


def create_random_date():
    return create_random_datetime().date()


def create_random_time():
    return create_random_datetime().time()

def create_random_float():
    return random.random() * random.randint(1, 10)


def create_random_decimal():
    return D(create_random_float())


def create_random_duration():
    return timedelta(
        days=random.randint(0, 28),
        seconds=random.randint(0, 59),
        microseconds=random.randint(0, 999),
        milliseconds=random.randint(0, 999),
        minutes=random.randint(0, 59),
        hours=random.randint(0, 23),
        weeks=random.randint(0, 54),
    )


def create_random_base_url(max_length=20):
    length = create_random_length(3, max_length)
    suffixs = ['de', 'com', 'net', 'org']
    suffix = suffixs[random.randint(0, len(suffixs) - 1)]
    return f'{create_random_char(length)}.{suffix}'

def create_random_url(max_length=10):
    num_parts = random.randint(0, 5)
    parts = '/'.join([str(create_random_length(1, 20)) for _ in range(0, num_parts)])
    return f'https://www.{create_random_base_url(max_length)}/{parts}'

def create_random_email():
    return f'{create_random_char(10)}@{create_random_base_url(25)}'


#file = models.FileField
#filepath = models.FilePathField('Filepath')

def create_random_ipaddress():
    def random_ipv4():
        return '.'.join(str(random.randint(0, 255)) for _ in range(4))
    def random_ipv6():
        return ':'.join('{:x}'.format(random.randint(0, 2**16 - 1)) 
                        for _ in range(8))
    return [random_ipv4, random_ipv6][random.randint(0, 1)]()


def create_random_integer(min_value=-99999, max_value=99999):
    return random.randint(min_value, max_value)


def create_random_json():
    return {'data': {'not_random': True}}


def create_random_positivebiginteger(max_value=99999):
    return create_random_integer(min_value=0, max_value=max_value)


def create_random_positiveinteger(max_value=99999):
    return create_random_integer(min_value=0, max_value=max_value)


def create_random_positivesmallinteger(max_value=255):
    return create_random_integer(min_value=0, max_value=max_value)


def create_random_smallinteger(min_value=-255, max_value=255):
    return create_random_integer(min_value=min_value, max_value=max_value)


def create_random_uuid():
    return uuid.uuid4()
