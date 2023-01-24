from django.db import models
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from htmx_viewsets.helpers import timer
from .create_random import *

MAIN_COUNT = 100000
PARENT_COUNT = 100
ATTRIBUTE_COUNT = 100
TAG_COUNT = 100
MAX_CHILDS = 100


class NamedModel(models.Model):
    name = models.CharField('Name', max_length=10, default=create_random_char)

    @classmethod
    def create_n(cls, count, **kwargs):
        instances =[cls(name=create_random_char(), **kwargs)
                    for _ in range(0, count)]
        cls.objects.bulk_create(instances)
        return cls.objects.all()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Tag(NamedModel): pass


class Attribute(NamedModel): pass


class Parent(NamedModel): pass


class Child(NamedModel):
    main = models.ForeignKey('Main', on_delete=models.CASCADE)


class AttributeValue(models.Model):
    main = models.ForeignKey('Main', on_delete=models.CASCADE)
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='attribute_values',
    )
    value = models.CharField('Value', max_length=10)

    @classmethod
    def create_n(cls, count, **kwargs):
        instances =[cls(value=create_random_char(), **kwargs)
                    for _ in range(0, count)]
        cls.objects.bulk_create(instances)
        return cls.objects.all()


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

    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)

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

    @staticmethod
    @timer
    def add_parents():
        return Parent.create_n(PARENT_COUNT)

    @classmethod
    @timer
    def create_instances(cls, parents, count):
        instances = [cls(parent=parents[randint(0, len(parents)-1)])
                for _ in range(0, count)]
        cls.objects.bulk_create(instances)
        return cls.objects.all()

    @classmethod
    @timer
    def add_tags(cls, instances, count=TAG_COUNT):
        tags = Tag.create_n(count)
        tags_to_add = []
        for instance in instances:
            for tag in tags:
                add_tag = [True, False][randint(0, 1)]
                if add_tag:
                    tags_to_add.append(
                        Main.tags.through(main=instance, tag=tag))
        cls.tags.through.objects.bulk_create(tags_to_add)

    @staticmethod
    @timer
    def add_childs(instances):
        childs_to_add = []
        for instance in instances:
            for _ in range(0, MAX_CHILDS):
                add_child = [True, False][randint(0, 1)]
                if add_child:
                    childs_to_add.append(
                        Child(main=instance,name=create_random_char())
                    )
        Child.objects.bulk_create(childs_to_add)
    
    @staticmethod
    @timer
    def add_attribute_values(instances):
        attributes = Attribute.create_n(ATTRIBUTE_COUNT)
        attributes_to_add = []
        for instance in instances:
            for attribute in attributes:
                add_attribute = [True, False][randint(0, 1)]
                if add_attribute:
                    attributes_to_add.append(
                        AttributeValue(
                            value=create_random_char(),
                            main=instance,
                            attribute=attribute)
                        )
        AttributeValue.objects.bulk_create(attributes_to_add)

    @classmethod
    def create_n(cls, count=MAIN_COUNT):
        parents = cls.add_parents()
        instances = cls.create_instances(parents, count)
        cls.add_tags(instances)
        cls.add_childs(instances)
        cls.add_attribute_values(instances)
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