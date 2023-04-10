from django.db import models
from django.db.models.functions.datetime import TruncDay, TruncHour,\
    TruncMinute, TruncSecond, ExtractWeekDay, ExtractIsoWeekDay, ExtractWeek,\
    ExtractQuarter
from django.utils.translation import gettext_lazy as _
from .color import Colors


INTEGER_MODEL_FIELDS = (
    models.IntegerField,
    models.PositiveBigIntegerField,
    models.PositiveIntegerField,
    models.PositiveSmallIntegerField,
    models.SmallIntegerField,
    models.BigIntegerField,
)

FLOAT_MODEL_FIELDS = (
    models.DecimalField,
    models.FloatField,
)

NUMBER_MODEL_FIELDS = (
    *INTEGER_MODEL_FIELDS,
    *FLOAT_MODEL_FIELDS,
)

ISO_DAY_NAMES = [
    _('Montag'),
    _('Dienstag'),
    _('Mittwoch'),
    _('Donnerstag'),
    _('Freitag'),
    _('Samstag'),
    _('Sonntag'),
]

DAY_NAMES = [
    ISO_DAY_NAMES[6],
    ISO_DAY_NAMES[0:5],
]

LOOKUP_CLEAN_FUNC = {  # ToDo: not yet working
    TruncDay:           lambda x: x.strftime('%d.%m.%Y'),
    TruncHour:          lambda x: x.strftime('%d.%m.%Y %H'),
    TruncMinute:        lambda x: x.strftime('%d.%m.%Y %H:%M'),
    TruncSecond:        lambda x: x.strftime('%d.%m.%Y %H:%M:%S'),
    ExtractWeekDay:     lambda x: DAY_NAMES[x-1],
    ExtractIsoWeekDay:  lambda x: ISO_DAY_NAMES[x-1],
    ExtractWeek:        lambda x: f'KW{x}',
    ExtractQuarter:     lambda x: f'Q{(x.month + 3 - 1) // 3}',
}


class ViewsetModelField:
    color_manager = Colors()
    allowed_data_fields = NUMBER_MODEL_FIELDS
    clean_func = LOOKUP_CLEAN_FUNC

    def __init__(self, model_field, qs):
        assert isinstance(model_field, models.Field)
        self.name               = model_field.name
        self.queryset           = qs
        self.model_field        = model_field
        self.form_field         = model_field.formfield()
        self.main_color         = self.get_color().rgb_str
        self.boder_color        = self.get_color().rgb_str
        self.background_color   = self.get_color().rgb_str
        self.color              = self.get_color().rgb_str
        self.verbose_name       = self.get_verbose_name()
        self.group_by           = qs.query.group_by

    def get_color(self):
        column = getattr(self.model_field, 'column', None)
        return self.color_manager.by_code(column)

    def clean_value(self, value):
        """
        ToDo: Implement clean func.
        """
        return value

    def get_verbose_name(self):
        return str(self.name)

    def get_lookups(self, only_groupable=False):
        """
        only_groupable: get only lookups that can be used in group by
        """
        lookups = []
        verbose_name = self.model_field.verbose_name
        if only_groupable and not self.model_field.primary_key:
            lookups.append((
                self.name,
                verbose_name,
            ))
        for name, lookup in self.model_field.get_lookups().items():
            is_groupable = issubclass(lookup, models.lookups.Transform)
            if not only_groupable or is_groupable:
                lookups.append((
                    f'{self.name}__{name}',
                    f'{verbose_name}: {lookup.__name__}',
                ))
            if hasattr(lookup, 'get_lookups'):
                for sub_name, sub_lookup in lookup.get_lookups().items():
                    is_groupable = issubclass(sub_lookup, models.lookups.Transform)
                    if not only_groupable or is_groupable:
                        lookups.append((
                            f'{self.name}__{name}__{sub_name}',
                            f'{verbose_name}: {sub_lookup.__name__}',
                        ))
        return lookups

    def get_group_by_lookups(self):
        return self.get_lookups(only_groupable=True)
