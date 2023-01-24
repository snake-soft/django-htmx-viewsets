import json
from typing import Iterable, Optional, Dict, Any
from django.db import models
from django.template.loader import get_template
from django.urls.base import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.http.request import HttpRequest
from . import row, plugins, action
from django.db.models.query import QuerySet


__all__ = ['Table']


class Table:
    codes: Iterable[str] = None
    ajax_url: Optional[str] = None

    template_name: str = 'htmx_viewsets/table.html'
    table_id: str = 'table'
    table_classes: str = 'table table-striped table-sm display align-middle h-100 w-100'
    table_styles: str = 'width:100%;overflow-y:scroll;'
    plugin_classes: Iterable[plugins.FieldsPlugin] = [
        plugins.FieldsPlugin,
    ]
    row_actions = [
        action.DetailRowAction,
        action.EditRowAction,
        action.DeleteRowAction,
    ]
    length_menu = json.dumps([
        [10, 25, 50, 100, 250, 500, 1000],
        [10, 25, 50, 100, 250, 500, 1000],
    ])
    show_footer = False

    def __init__(self, request: HttpRequest, queryset: models.Model,
                 url_names: Dict[str, str], codes: Optional[Iterable[str]]=None,
                 **kwargs: Optional[Dict[str, Any]]) -> None:

        self.request = request
        assert isinstance(queryset, QuerySet)
        self._queryset = queryset
        self.model = queryset.model

        self.url_names = url_names
        self.search_query = request.GET.get('search[value]')

        self.codes = codes or [x.name for x in self.model._meta.fields]

        assert self.codes

        self.plugins = self.get_plugins(self._queryset, self.plugin_classes, self.codes)
        self.columns = self.get_columns(self.plugins)
        self.queryset = self.get_result_qs(
            request, self.columns, self._queryset, self.search_query)
        self.paginator = self.get_paginator(request, self.queryset)
        self.page = self.get_page(request, self.paginator)
        self.rows = self.get_rows(
            self.page.object_list, self.codes, self.row_actions)
        self.verbose_name = self.model._meta.verbose_name
        self.verbose_name_plural = self.model._meta.verbose_name_plural

    @staticmethod
    def get_paginator(request, result_qs):
        per_page = request.GET.get('length', '10')
        return Paginator(result_qs, int(per_page))

    @staticmethod
    def get_page(request, paginator):
        per_page = paginator.per_page
        offset = int(request.GET.get('start', 0))
        page_nr = (offset + per_page) / per_page
        return paginator.get_page(page_nr)

    @staticmethod
    def get_plugins(model, plugin_classes, codes):
        return  [cls(model, codes) for cls in plugin_classes]

    @staticmethod
    def get_columns(plugins):
        columns = []
        for plugin in plugins:
            for column in plugin.columns:
                columns.append(column)
        return columns

    @staticmethod
    def get_result_qs(request, columns, qs, search_query):
        query = Q()
        for column in columns:
            column_query = column.get_query(qs, search_query)
            if column_query:
                query |= column.get_query(qs, search_query)
        if query:
            qs = qs.filter(query)
        order_column = request.GET.get('order[0][column]', None)
        if order_column:
            order_column = columns[int(order_column)]
            order_desc = request.GET.get('order[0][dir]') == 'desc'
            order_code = f'-{order_column.code}' if order_desc \
                else order_column.code
            qs = qs.order_by(order_code)
        return qs

    @property
    def ajax_url(self):
        base_url = reverse(self.url_names["table"])
        return f'{base_url}?{self.request.GET.urlencode()}'

    @property
    def list_url(self):
        base_url = reverse(self.url_names['list'])
        return f'{base_url}?{self.request.GET.urlencode()}'

    @property
    def data(self):
        data = {
            "draw": int(self.request.GET.get('draw', 1)) + 1,
            "recordsTotal": self._queryset.count(),
            "recordsFiltered": self.queryset.count(),
            "data": [row.data for row in self.rows],
        }
        return data

    def get_rows(self, object_list, codes, row_actions):
        return [row.Row(self, self.queryset, instance, codes, row_actions, self.url_names)
                for instance in object_list]

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
