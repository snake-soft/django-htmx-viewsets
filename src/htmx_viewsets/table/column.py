from abc import ABC

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from ..fields import ViewsetModelField
from .cell import Cell, ActionCell


__all__ = ['Column']


class ColumnBase(ABC):
    name = ''
    verbose_name = ''
    cell_class = Cell
    is_pk = False

    def get_query(self, *args):
        return {}

    def __str__(self):
        return str(self.verbose_name)

    def __repr__(self):
        return 'Col: ' + str(self)


class Column(ColumnBase):
    def __init__(self, viewset_field:ViewsetModelField) -> None:
        self.viewset_field = viewset_field
        self.model_field = viewset_field.model_field
        self.is_pk = viewset_field.model_field.primary_key
        self.name = viewset_field.name
        self.verbose_name = viewset_field.verbose_name

    def get_query(self, queryset:QuerySet, search_query:str) -> Q:
        if not search_query:
            return None

        q_kwargs = {}
        if isinstance(self.model_field, models.BigAutoField):
            if search_query is not None and search_query.isdigit():
                q_kwargs = {self.model_field.name: int(search_query)}
            else:
                q_kwargs = {} # not possible
        if isinstance(self.model_field, models.CharField):
            q_kwargs = {self.model_field.name + '__icontains': search_query}
        
        if isinstance(self.model_field, (models.ForeignKey, models.DateTimeField)):
            q_kwargs = {} # not implemented

        if q_kwargs is None:
            print(str(self.model_field.__class__) + 'not yet implemented')
        return Q(**q_kwargs) if q_kwargs else None



class ActionColumn(ColumnBase):
    cell_class = ActionCell
    viewset_field = None
