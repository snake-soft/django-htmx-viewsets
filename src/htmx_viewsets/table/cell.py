from django.db.models import fields
from django.db.models.query import QuerySet

__all__ = ['Cell']


class Cell:
    def __init__(self, queryset, instance, code):
        assert isinstance(queryset, QuerySet)
        self.instance = instance
        assert instance
        self.code = code
        self.field = queryset.model._meta.get_field(code)

    def __str__(self):
        try:
            value = getattr(self.instance, self.code, None)
        except AttributeError:
            value = self.instance[self.code]
        if value is None:
            return '<i class="fa-solid fa-ban text-warning"></i>'

        if isinstance(self.field, fields.related.ManyToManyField):
            manager = getattr(self.instance, self.code)
            return ', '.join([str(x) for x in manager.all()])

        if isinstance(self.field, fields.BooleanField):
            return {
                True: '<i class="fa-solid fa-check text-success"></i>',
                False: '<i class="fa-solid fa-xmark text-danger"></i>',
                None: '<i class="fa-solid fa-question"></i>',
            }[value]
        
        max_length = 25
        value = str(value)
        if len(value) > max_length:
            try:
                value = value[:max_length] + '...'
            except TypeError:
                pass
        return f'<span class="cell">{value}</span>'
