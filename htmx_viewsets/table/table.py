from typing import Iterable, Optional, ClassVar
from django.db import models
from django.template.loader import get_template
from django.urls.base import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from . import row, plugins, action


__all__ = ['Table']


class Table:
    codes: Iterable = None
    ajax_url: Optional[str] = None

    template_name: str = 'htmx_viewsets/table.html'
    table_id: str = 'table'
    table_classes: str = 'table table-striped display'
    table_styles: str = 'width:100%'
    plugin_classes: Iterable = [
        plugins.FieldsPlugin,
    ]
    row_actions = [
        action.DetailRowAction,
        action.EditRowAction,
        action.DeleteRowAction,
    ]
    options = {}
    url_mapping = {}
    show_footer = False

    def __init__(self, request, qs, codes=None, **kwargs):
        self.request = request
        self.qs = qs
        self.model = qs.model
        self.search_query = request.GET.get('search[value]')

        self.codes = [x.name for x in qs.model._meta.fields] if codes is None \
            else codes

        for key, value in kwargs.items():
            setattr(self, key, value)

        assert self.codes
        self.plugins = self.get_plugins(self.plugin_classes, self.codes)
        self.columns = self.get_columns(self.plugins)
        self.result_qs = self.get_result_qs(self.qs, self.search_query)
        self.paginator = self.get_paginator(request)
        self.rows = self.get_rows(self.result_qs, self.codes, self.row_actions)
        self.page = self.get_page(request, self.paginator)
        self.verbose_name = self.model._meta.verbose_name
        self.verbose_name_plural = self.model._meta.verbose_name_plural

    def get_paginator(self, request):
        return Paginator([*self.result_qs], int(request.GET.get('length', 10)))

    def get_page(self, request, paginator):
        per_page = paginator.per_page
        offset = int(request.GET.get('start', 0))
        page_nr = (offset + per_page) / per_page
        return paginator.get_page(page_nr)

    @property
    def ajax_url(self):
        namespace = self.request.resolver_match.namespace
        model_name = self.model._meta.model_name
        return reverse(f'{namespace}:{model_name}-table')

    @property
    def list_url(self):
        namespace = self.request.resolver_match.namespace
        model_name = self.model._meta.model_name
        return reverse(f'{namespace}:{model_name}-list')

    def get_plugins(self, plugin_classes, codes):
        return  [cls(self.model, codes) for cls in plugin_classes]

    def get_columns(self, plugins):
        columns = []
        for plugin in plugins:
            for column in plugin.columns:
                columns.append(column)
        return columns

    def get_rows(self, instances, codes, row_actions):
        return [row.Row(self, instance, codes, row_actions)
                for instance in instances]

    def get_context_data(self):
        return {
            'table': self,
            'paginator': self.paginator,
            'page_obj': self.page,
            'is_paginated': self.page.has_other_pages(),
            'object_list': self.result_qs,
        }

    def get_result_qs(self, qs, search_query):
        query = Q()
        for column in self.columns:
            column_query = column.get_query(qs, search_query)
            if column_query:
                query |= column.get_query(qs, search_query)
        qs = qs.filter(query)
        order_column = self.request.GET.get('order[0][column]', None)
        if order_column:
            order_column = self.columns[int(order_column)]
            order_desc = self.request.GET.get('order[0][dir]') == 'desc'
            order_code = f'-{order_column.code}' if order_desc \
                else order_column.code
            qs = qs.order_by(order_code)
        return qs

    def render(self, *args, **kwargs):
        return get_template(self.template_name).render(self.get_context_data())

    def render_actions(self, *args, **kwargs):
        return ''.join([action.render() for action in self.row_actions])

    @property
    def data(self):
        data = {
            "draw": int(self.request.GET.get('draw', 1)) + 1,
            "recordsTotal": self.qs.count(),
            "recordsFiltered": self.paginator.count,
            "data": [row.data for row in self.rows],
        }
        return data
