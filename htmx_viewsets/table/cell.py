from django.db.models import fields

__all__ = ['Cell']


class Cell:
    def __init__(self, instance, code):
        self.instance = instance
        self.code = code
        self.field = self.instance.__class__._meta.get_field(code)

    def __str__(self):
        if isinstance(self.field, fields.related.ManyToManyField):
            manager = getattr(self.instance, self.code)
            return ', '.join([str(x) for x in manager.all()])
        return str(getattr(self.instance, self.code))
