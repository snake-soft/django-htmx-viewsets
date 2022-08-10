from typing import Iterable
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls.conf import path
from django.db import models
from django.utils.functional import classproperty
from django.views.generic.base import View, ContextMixin
from .table import Table
from . import views


class HtmxModelViewSet:
    list_view_class:View = views.HtmxListView
    detail_view_class:View = views.HtmxDetailView
    create_view_class:View = views.HtmxCreateView
    update_view_class:View = views.HtmxUpdateView
    delete_view_class:View = views.HtmxDeleteView
    table_view_class:View = views.JsonTableView

    full_template_name: str = views.HtmxListView.template_name
    partial_template_name: str = views.HtmxListView.template_name

    list_template_name: str = views.HtmxListView.template_name
    detail_template_name: str = views.HtmxDetailView.template_name
    create_template_name: str = views.HtmxCreateView.template_name
    update_template_name: str = views.HtmxUpdateView.template_name
    delete_template_name: str = views.HtmxDeleteView.template_name
    table_template_name: str = views.JsonTableView.template_name

    view_codes: Iterable = [
        'list', 'detail', 'create', 'update', 'delete', 'table']

    path_mapping = {
        'list': '',
        'detail': '<int:pk>/',
        'create': 'create/',
        'update': '<int:pk>/update/',
        'delete': '<int:pk>/delete/',
        'table': 'table/',
    }
    node_id: str = 'main'

    list_fields: Iterable = None
    detail_fields: Iterable = None
    create_fields: Iterable = None
    update_fields: Iterable = None
    fields: Iterable = None  # overwrites other fields

    create_form_class: Iterable = None
    update_form_class: Iterable = None
    form_class: Iterable = None  # overwrites other form_classes

    model: models.Model
    namespace: str
    inline_fieldsets = []

    @classmethod
    def get_view_class(cls, code):
        view_class = getattr(cls, f'{code}_view_class')
        full_template_name = getattr(
            cls, f'{code}_template_name', cls.full_template_name)

        form_class = getattr(cls, f'{code}_form_class', 
                             getattr(cls, 'form_class', None))

        fields = getattr(cls, 'fields', getattr(
            cls, f'{code}_fields', cls.model._meta.fields))

        kwargs = {
            'form_class': form_class,
            'full_template_name': cls.full_template_name,
            'partial_template_name': cls.partial_template_name,

            # Table only:
            'model': cls.model,
            'fields': fields,
            'node_id': cls.node_id,
            'create_url': cls.url_names['create'],
        }
        result = type(view_class.__name__, (view_class,), kwargs)
        return result

    @classproperty
    def url_names(cls):  # @NoSelf
        model_name = cls.model._meta.model_name
        return {code: f'{model_name}-{code}' for code in cls.view_codes}

    @classproperty
    def urls(cls):  # @NoSelf
        urls = []
        for code in cls.view_codes:
            view = cls.get_view_class(code)
            url_name = cls.url_names[code]
            urls.append(
                path(cls.path_mapping[code], view.as_view(), name=url_name))
        return urls


class HtmxModelInlineViewSet(HtmxModelViewSet):
    pass
