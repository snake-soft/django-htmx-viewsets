from random import randint, random
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from decimal import Decimal as D
import json
import ipaddress
from django.utils.text import slugify
import uuid
from datetime import timedelta

MAX_IPV4 = ipaddress.IPv4Address._ALL_ONES  # 2 ** 32 - 1
MAX_IPV6 = ipaddress.IPv6Address._ALL_ONES  # 2 ** 128 - 1


def create_random_length(min_length, max_length):
    choices = range(min_length, max_length)
    return choices[randint(0, len(choices) - 1)]


def create_random_boolean():
    return randint(0, 1)


def create_random_binary(length=50):
    for i in range(length):
        return bytes([create_random_boolean() for _ in range(length)])


def create_random_char(length=10):
    return get_random_string(length=length)


def create_random_slug(length=10):
    return slugify(create_random_char(length=length))


def create_random_text(min_length=0, max_length=100):
    length = randint(min_length, max_length)
    return create_random_char(length=length)


def create_random_date():
    return now().date()


def create_random_datetime():
    return now()


def create_random_decimal():
    return D(random()*99)


def create_random_duration():
    return timedelta(
        days=randint(0, 28),
        seconds=randint(0, 59),
        microseconds=randint(0, 999),
        milliseconds=randint(0, 999),
        minutes=randint(0, 59),
        hours=randint(0, 23),
        weeks=randint(0, 54),
    )


def create_random_base_url(max_length=20):
    length = create_random_length(3, max_length)
    suffixs = ['de', 'com', 'net', 'org']
    suffix = suffixs[randint(0, len(suffixs) - 1)]
    return f'{create_random_char(length)}.{suffix}'

def create_random_url(max_length=10):
    num_parts = randint(0, 5)
    parts = '/'.join([str(create_random_length(1, 20)) for _ in range(0, num_parts)])
    return f'https://www.{create_random_base_url(max_length)}/{parts}'

def create_random_email():
    return f'{create_random_char(10)}@{create_random_base_url(25)}'


#file = models.FileField
#filepath = models.FilePathField('Filepath')
def create_random_float():
    return random()


def create_random_ipaddress():
    def random_ipv4():
        return  ipaddress.IPv4Address._string_from_ip_int(
            randint(0, MAX_IPV4)
        )
    
    def random_ipv6():
        return ipaddress.IPv6Address._string_from_ip_int(
            randint(0, MAX_IPV6)
        )

    func = [random_ipv4, random_ipv6][randint(0, 1)]
    return func()


#image = models.ImageField
def create_random_integer(min_value=-99999, max_value=99999):
    return randint(min_value, max_value)


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

def create_random_time():
    return now().time()


def create_random_uuid():
    return uuid.uuid4()
