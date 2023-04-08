import json
from typing import Dict

from django.template.loader import get_template
from django.urls.base import reverse
from django.db.models import Q, QuerySet
from django.core.paginator import Paginator

from .column import Column, ActionColumn
from .row import Row
from .action import DeleteRowAction, DetailRowAction, EditRowAction


__all__ = ['Table']


class Table:
    template_name: str = 'htmx_viewsets/table.html'
    table_id: str = 'table'
    table_classes: str = 'table table-striped table-sm display align-middle h-100 w-100'
    table_styles: str = 'width:100%;overflow-y:scroll;'
    row_action_classes = [
        DetailRowAction,
        EditRowAction,
        DeleteRowAction,
    ]
    length_menu = json.dumps([
        [10, 50, 250, 1000],
        [10, 50, 250, 1000],
    ])
    show_footer = False

    def __init__(self, request, qs, viewset_fields, table_id,
                 url_names: Dict[str, str]):
        self.request_data = getattr(request, request.method)

        self.url_names = url_names
        self.base_queryset = qs

        self.fields = viewset_fields
        self.table_id = table_id
        self.verbose_name = qs.model._meta.verbose_name
        self.verbose_name_plural = qs.model._meta.verbose_name_plural

        self.queryset = self.get_qs(self.request_data, qs)
        self.paginator = self.get_paginator(self.request_data, self.queryset)
        self.page = self.get_page(self.request_data, self.paginator)
        self.columns = self.get_columns(self.queryset)

        self.row_action_classes = self.get_row_action_classes(self.columns)

        first = self.page.start_index()-1
        last = self.page.end_index()-1
        if first >= 0 and last >= 0:
            objects = self.queryset[first:last]
        else:
            objects = self.queryset.none()
        assert isinstance(objects, QuerySet)
        self.rows = self.get_rows(
            self.page.object_list, self.columns, url_names, self.row_action_classes)

    def get_fields(self, queryset):
        return self.fields

    def get_columns(self, qs):
        columns = []
        if self.row_action_classes and not qs.query.group_by:
            columns.append(ActionColumn())
        for field in self.fields:
            columns.append(Column(field))
        return columns

    def get_rows(self, objects, columns, url_names, row_action_classes):
        return [Row(columns, instance, url_names, row_action_classes)
                for instance in objects]

    def get_row_action_classes(self, columns):
        """
        Add Row action buttons if is instance
        """
        for column in columns:
            if column.is_pk:
                return self.row_action_classes
        return []

    def get_paginator(self, request_data, result_qs):
        per_page = request_data.get('length', '10')
        return Paginator(result_qs, int(per_page))

    def get_page(self, request_data, paginator):
        per_page = paginator.per_page
        offset = int(request_data.get('start', 0))
        page_nr = (offset + per_page) / per_page
        return paginator.get_page(page_nr)

    def filter_qs(self, request_data, qs):
        search_query = request_data.get('search[value]')
        query = Q()
        for column in self.get_columns(qs):
            column_query = column.get_query(qs, search_query)
            if column_query:
                query |= column.get_query(qs, search_query)
        if query:
            qs = qs.filter(query)
        return qs

    def order_qs(self, request_data, qs):
        columns = [*self.get_columns(qs)]
        order_column = request_data.get('order[0][column]', None)
        if order_column:
            order_column = columns[int(order_column)]
            order_desc = request_data.get('order[0][dir]') == 'desc'
            order_code = f'-{order_column.name}' if order_desc \
                else order_column.name
            if order_code:
                qs = qs.order_by(order_code)
        return qs

    def get_qs(self, request_data, qs):
        qs = self.filter_qs(request_data, qs)
        qs = self.order_qs(request_data, qs)
        return qs

    @property
    def ajax_url(self):
        base_url = reverse(self.url_names["table"])
        return f'{base_url}?{self.request_data.urlencode()}'

    @property
    def list_url(self):
        base_url = reverse(self.url_names['list'])
        return f'{base_url}?{self.request_data.urlencode()}'

    @property
    def data(self):
        data = {
            "draw": int(self.request_data.get('draw', 1)) + 1,
            "recordsTotal": self.base_queryset.count(),
            "recordsFiltered": self.queryset.count(),
            "data": [row.data for row in self.rows],
        }
        return data

    def get_row(self, instance):
        rows = [*self.get_rows([instance], self.columns, self.url_names, self.row_action_classes)]
        return rows[0]
        for row in self.rows:
            if row.instance==instance:
                return row
        raise AttributeError('Row for instance not found: ' + str(instance))

    def get_context_data(self):
        ctx = {
            'table': self,
            'paginator': self.paginator,
            'page_obj': self.page,
            'is_paginated': self.page.has_other_pages(),
            'object_list': self.queryset,
        }
        return ctx

    def render(self, *args, **kwargs):
        return get_template(self.template_name).render(self.get_context_data())

    def render_actions(self, *args, **kwargs):
        return ''.join([action.render() for action in self.row_actions])
