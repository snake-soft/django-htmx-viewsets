import random
import itertools
from collections import Iterable, Callable
from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import Parent, Tag, Main, Child, Attribute, AttributeValue


# Main_n
MAIN_COUNT = 1000000

# Parent_n
PARENT_COUNT = 100

# MAIN_COUNT * ATTRIBUTE_COUNT * PROPABILITY = AttributeValue_n  
ATTRIBUTE_COUNT = 100
ATTRIBUTE_VALUES_PROPABILITY = 0.1

# MAIN_COUNT * TAG_COUNT * PROPABILITY = Main.tags_n
TAG_COUNT = 100  # Tags_n
MAIN_TAG_PROPABILITY = 0.1

# MAIN_COUNT * MAX_CHILDS * CHILD_PROPABILITY = Main.childs_n
MAX_CHILDS = 10
CHILD_PROPABILITY = 1

CHUNK_SIZE = 1000
BOOST = False  # 10


class Command(BaseCommand):
    help = 'Create database with random objects'

    def add_arguments(self, parser):
        parser.add_argument(
            'model_names',
            nargs='*',
            default=['main', 'parent', 'attribute', 'tag', 'child'],
            help='Models to create',
        )
        parser.add_argument(
            '-c'
            '--count',
            dest='count',
            type=int,
            help='Overwrite all count fields',
        )
        parser.add_argument(
            '-p'
            '--propability',
            dest='propability',
            type=float,
            help='Overwrite all propability fields',
        )
        parser.add_argument(
            '--main',
            dest='main_count',
            type=int,
            default=BOOST or MAIN_COUNT,
        )
        parser.add_argument(
            '--parent',
            dest='parent_count',
            type=int,
            default=BOOST or PARENT_COUNT,
        )
        parser.add_argument(
            '--attribute',
            dest='attribute_count',
            type=int,
            default=BOOST or ATTRIBUTE_COUNT,
        )
        parser.add_argument(
            '--attribute-propability',
            type=float,
            default=ATTRIBUTE_VALUES_PROPABILITY,
        )
        parser.add_argument(
            '--tag',
            dest='tag_count',
            type=int,
            default=BOOST or TAG_COUNT,
        )
        parser.add_argument(
            '--tag-propability',
            type=float,
            default=MAIN_TAG_PROPABILITY,
        )
        parser.add_argument(
            '--child',
            dest='child_count',
            type=int,
            default=BOOST or MAX_CHILDS,
        )
        parser.add_argument(
            '--child-propability',
            type=float,
            default=CHILD_PROPABILITY,
        )
        parser.add_argument(
            '-w', '--write',
            help='Write to db',
            action='store_true',
            dest='write',
        )

    @classmethod
    def _clean_value(cls, value):
        if isinstance(value, Iterable):
            value = value[random.randint(0, len(value)-1)]
        if isinstance(value, Callable):
            value = value()
        return value

    @classmethod
    def _clean_kwargs(cls, **kwargs):
        return {key: cls._clean_value(value) for key, value in kwargs.items()}

    @classmethod
    def _generate_instances(cls, model, count, **kwargs):
        for _ in range(0, count):
            kwargs = cls._clean_kwargs(**kwargs)
            yield model(**kwargs)

    @classmethod
    def create_n(cls, model, count, **kwargs):
        objs = cls._generate_instances(model, count, **kwargs)
        cls.create_from_generator(model, objs, CHUNK_SIZE)

    @staticmethod
    def create_from_generator(model, generator, chunk_size):
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
        #generator = [*generator]
        #print(f'{str(model.__name__)}: {str(len(generator))}x')
        #generator = (x for x in generator)
        
        while True:
            batch = list(itertools.islice(generator, chunk_size))
            if not batch:
                break
            model.objects.bulk_create(batch, chunk_size)

    @staticmethod
    def clean_model_names(model_names) -> set:
        return set(model_names)

    @classmethod
    def create_parents(cls, count):
        cls.create_n(Parent, count)

    @classmethod
    def create_mains(cls, parents, count):
        parents = parents.values_list('id', flat=True)
        cls.create_n(Main, count, parent_id=parents)

    @classmethod
    def create_tags(cls, count):
        cls.create_n(Tag, count)

    @staticmethod
    def combine(model, *args, **kwargs):
        for values in itertools.product(*kwargs.values()):
            yield model(**dict(zip(kwargs.keys(), values)))

    @staticmethod
    def propability(iterable, propability):
        for value in iterable:
            if random.random() < propability:
                yield value

    @classmethod
    def add_tags(cls, mains, tags, propability):
        model = Main.tags.through
        mains = mains.values_list('pk', flat=True)
        tags = tags.values_list('pk', flat=True)
        generator = cls.propability(
            cls.combine(model, main_id=mains, tag_id=tags),
            propability,
        )
        cls.create_from_generator(model, generator, CHUNK_SIZE)

    @classmethod
    def create_childs(cls, main_instances, count, propability):
        count = main_instances.count() * count
        main_ids = list(main_instances.values_list('pk', flat=True))
        mains = (Child(main_id=random.choice(main_ids)) for _ in range(0, count))
        mains = cls.propability(mains, propability)
        cls.create_from_generator(Child, mains, CHUNK_SIZE)

    @classmethod
    def create_attributes(cls, count):
        cls.create_n(Attribute, count)

    @classmethod
    def add_attribute_values(cls, main_instances, attributes, propability):
        mains = main_instances.values_list('pk', flat=True).iterator()
        attributes = attributes.values_list('pk', flat=True).iterator()
        model = AttributeValue
        generator = cls.propability(
            cls.combine(model, main_id=mains, attribute_id=attributes),
            propability,
        )
        cls.create_from_generator(model, generator, CHUNK_SIZE)

    def create(self, model_names, count, main_count, parent_count,
                      tag_count, attribute_count, child_count,
                      propability, child_propability, **options):
        link_models = {*model_names}
        if 'parent' in model_names:
            self.create_parents(count or parent_count)

        if 'main' in model_names:
            parents = Parent.objects.filter(mains=None)
            if not parents.exists():
                parents = Parent.objects.all()
            assert parents.exists()
            self.create_mains(parents, count or main_count)
            link_models.add('tag')
            link_models.add('child')
            link_models.add('attribute')

        if 'tag' in model_names:
            self.create_tags(count or tag_count)

        if 'attribute' in model_names:
            self.create_attributes(count or attribute_count)

        if 'child' in model_names:
            mains = Main.objects.filter(childs=None)
            self.create_childs(
                mains,
                count or child_count,
                propability or child_propability,
            )
        return link_models

    def link(self, model_names, propability, attribute_propability,
                    tag_propability, child_propability, **options):
        if 'tag' in model_names:
            #mains = Main.objects.all()
            mains = Main.objects.filter(tags=None)
            tags = Tag.objects.filter(mains=None)
            self.add_tags(mains, tags, propability or tag_propability)

        if 'attribute' in model_names:
            mains = Main.objects.filter(attribute_values=None)
            attributes = Attribute.objects.filter(attribute_values=None)
            self.add_attribute_values(
                mains,
                attributes,
                propability or attribute_propability,
            )

    @transaction.atomic
    def handle(self, *, model_names, write, **options):
        create_models = self.clean_model_names(model_names)
        link_models = self.create(create_models, **options)
        self.link(link_models, **options)
        if not write:
            raise AttributeError('Success but avoid saving.')
