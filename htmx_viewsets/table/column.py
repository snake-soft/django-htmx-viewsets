from django.db.models import fields
from django.db.models import Q


__all__ = ['Column']


class Column:
    def __init__(self, model, code, name=None):
        self.model = model
        self.code = code
        self.name = name or self.get_name()

    def get_name(self):
        return self.model._meta.get_field(self.code).verbose_name

    def get_query(self, qs, search_query):
        if not search_query:
            return None

        field = qs.model._meta.get_field(self.code)
        q_kwargs = {}
        if isinstance(field, fields.BigAutoField):
            if search_query is not None and search_query.isdigit():
                q_kwargs = {self.code: int(search_query)}
            else:
                q_kwargs = {} # not possible
        if isinstance(field, fields.CharField):
            q_kwargs = {self.code + '__icontains': search_query}
        
        if isinstance(field, (fields.related.ForeignKey, fields.DateTimeField, )):
            q_kwargs = {} # not implemented
            
        
        
        if q_kwargs is None:
            print(str(field.__class__) + 'not yet implemented')
        return Q(**q_kwargs) if q_kwargs else None

    def __repr__(self):
        return 'Col: ' + str(self)

    def __str__(self):
        return str(self.name)
