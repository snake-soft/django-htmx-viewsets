from django.db import models
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from htmx_viewsets.helpers import timer
from .create_random import *


# Main_n
MAIN_COUNT = 100000

# Parent_n
PARENT_COUNT = 1000

# Main_n * Attribute_n * ATTRIBUTE_VALUES_PROPABILITY = AttributeValue_n
ATTRIBUTE_COUNT = 1000
ATTRIBUTE_VALUES_PROPABILITY = 0.1

# Main_n * Tags_n * TAG_MAIN_PROPABILITY = Main.tags_n
TAG_COUNT = 1000  # Tags_n
MAIN_TAG_PROPABILITY = 0.1

# Main_n * MAX_CHILDS * 0,5 = Main.childs_n
MAX_CHILDS = 1000
CHILD_PROPABILITY = 0.1

CHUNK_SIZE = 100000


class NamedModel(models.Model):
    name = models.CharField(
        'Name',
        max_length=10,
        default=create_random_char,
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Tag(NamedModel): pass


class Attribute(NamedModel): pass


class Parent(NamedModel): pass


class Child(NamedModel):
    main = models.ForeignKey(
        'Main',
        on_delete=models.CASCADE,
        related_name='childs',
    )


class AttributeValue(models.Model):
    main = models.ForeignKey(
        'Main',
        on_delete=models.CASCADE,
        related_name='attribute_values',
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='attribute_values',
    )
    value = models.CharField(
        'Value',
        max_length=10,
        default=create_random_char,
    )


def get_random_parent():
    return Parent.objects.order_by('?').first()


class Main(NamedModel):
    attributes = models.ManyToManyField(
        Attribute,
        verbose_name='Attributes',
        through=AttributeValue,
        related_name='mains',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='mains',
    )
    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        default=get_random_parent,
        related_name='mains',
    )

    # Values
    #binary = models.BinaryField(
    #    'Binary',
    #    default=create_random_binary
    #)
    boolean = models.BooleanField(
        'Boolean',
        default=create_random_boolean,
    )
    char = models.CharField(
        'Char',
        max_length=10,
        default=create_random_char,
    )
    date = models.DateField(
        'date',
        default=create_random_date,
    )
    datetime = models.DateTimeField(
        'DateTime',
        default=create_random_datetime,
    )
    decimal = models.DecimalField(
        'Decimal',
        decimal_places=2, max_digits=4,
        default=create_random_decimal,
    )
    duration = models.DurationField(
        'Duration',
        default=create_random_duration,
    )
    email = models.EmailField(
        'Email',
        default=create_random_email,
    )
    #file = models.FileField
    #filepath = models.FilePathField('Filepath')
    float = models.FloatField(
        'Float',
        default=create_random_float,
    )
    ipaddress = models.GenericIPAddressField(
        'IP Address',
        default=create_random_ipaddress,
    )
    #image = models.ImageField
    integer = models.IntegerField(
        'Integer',
        default=create_random_integer,
    )
    json = models.JSONField(
        'Json',
        default=create_random_json,
    )
    positivebiginteger = models.PositiveBigIntegerField(
        'PositiveBigInteger',
        default=create_random_positivebiginteger,
    )
    positiveinteger = models.PositiveIntegerField(
        'PositiveInteger',
        default=create_random_positiveinteger,
    )
    positivesmallinteger = models.PositiveSmallIntegerField(
        'PositiveSmallInteger',
        default=create_random_positivesmallinteger,
    )
    slug = models.SlugField(
        'Slug',
        default=create_random_slug,
    )
    smallinteger = models.SmallIntegerField(
        'SmallInteger',
        default=create_random_smallinteger,
    )
    text = models.TextField(
        'Text',
        default=create_random_text,
    )
    time = models.TimeField(
        'Time',
        default=create_random_time,
    )
    url = models.URLField(
        'URL',
        default=create_random_url,
    )
    uuid = models.UUIDField(
        'UUID',
        default=create_random_uuid,
    )
    # Additional testcase fields:
    nullable = models.CharField(
        'Nullable',
        max_length=50,
        blank=True, null=True,
    )

    #@staticmethod
    #@timer
    #def add_parents():
    #    return Parent.create_n(PARENT_COUNT)

    #@classmethod
    #@timer
    #def create_instances(cls, parents):
    #    instances = []
    #    max_parent_i = len(parents)
    #    for i in range(1, MAIN_COUNT):
    #        instances.append(cls(parent=parents[randint(0, max_parent_i -1 )]))
    #        if not i % CHUNK_SIZE:
    #            cls.objects.bulk_create(instances, batch_size=CHUNK_SIZE)
    #            instances = []
    #            print(f'{i} of {MAIN_COUNT} Main created.')
    #    return cls.objects.all()

    #@classmethod
    #@timer
    #def add_tags(cls, instances, count=TAG_COUNT):
    #    tags = Tag.create_n(count)
    #    tags_to_add = []
    #    for instance in instances:
    #        for tag in tags:
    #            #add_tag = [True, False][randint(0, 1)]
    #            if random() <= MAIN_TAG_PROPABILITY:
    #                tags_to_add.append(
    #                    Main.tags.through(main=instance, tag=tag))
    #    return cls.tags.through.objects.bulk_create(tags_to_add)

    #@staticmethod
    #@timer
    #def add_childs(instances):
    #    childs_to_add = []
    #    for instance in instances:
    #        add_amount = MAX_CHILDS * random(0, CHILD_PROPABILITY)
    #        for i in range(0, randint(0, add_amount)):
    #            childs_to_add.append(
    #                Child(main=instance,name=create_random_char())
    #            )
    #    return Child.objects.bulk_create(childs_to_add)
    
    @staticmethod
    @timer
    def add_attribute_values(instances):
        attributes = Attribute.create_n(ATTRIBUTE_COUNT)
        attributes_to_add = []
        for instance in instances:
            for attribute in attributes:
                if random() <= ATTRIBUTE_VALUES_PROPABILITY:
                    attributes_to_add.append(
                        AttributeValue(
                            value=create_random_char(),
                            main=instance,
                            attribute=attribute)
                        )
        return AttributeValue.objects.bulk_create(attributes_to_add)

    @classmethod
    def create_n111(cls, count=MAIN_COUNT):
        parents = cls.add_parents()
        print(str(parents.count()) + ' Parent.')
        instances = cls.create_instances(parents)
        print(str(instances.count()) + ' Main.')
        print(str(len(cls.add_tags(instances))) + ' Main.tag.through.')
        print(str(len(cls.add_childs(instances))) + ' Child.')
        print(str(len(cls.add_attribute_values(instances))) + ' AttributeValue.')
        return instances

    class Meta:
        ordering = ['id']
        verbose_name = _('Main')

'''
    AutoField
    BigAutoField
    BigIntegerField
    BinaryField
    BooleanField
    CharField
    DateField
    DateTimeField
    DecimalField
    DurationField
    EmailField
    FileField
    FileField and FieldFile
    FilePathField
    FloatField
    GenericIPAddressField
    ImageField
    IntegerField
    JSONField
    PositiveBigIntegerField
    PositiveIntegerField
    PositiveSmallIntegerField
    SlugField
    SmallAutoField
    SmallIntegerField
    TextField
    TimeField
    URLField
    UUIDField
'''