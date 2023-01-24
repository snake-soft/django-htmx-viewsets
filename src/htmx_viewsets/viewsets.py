from abc import ABC, abstractmethod
from typing import Iterable, Optional
from django.urls.conf import path
from django.db import models
from django.utils.functional import classproperty
from htmx_viewsets.master import HtmxViewsetsMaster
from . import views, chart
from django.db.models.query import QuerySet
from htmx_viewsets.chart import MixedChart
from django import forms
from .forms import EnabledFilterForm, AddFilterForm, RemoveFilterForm


class HtmxViewSetBase(ABC):
    # Required:
    node_id:        str
    urls            : Iterable

    # Optional:
    master          : Optional = None
    base_template   : Optional[str] = 'htmx_viewsets/full.html'
    charts          : Iterable = []


class HtmxViewSet(HtmxViewSetBase):
    url_paths = {
        'list': '',
        'detail': '<int:pk>/',
        'create': 'create/',
        'update': '<int:pk>/update/',
        'delete': '<int:pk>/delete/',
        'table': 'table/',
        'chart': 'chart/',
    }
    view_classes = {
        'list': views.HtmxListView,
        'detail': views.HtmxDetailView,
        'create': views.HtmxCreateView,
        'update': views.HtmxUpdateView,
        'delete': views.HtmxDeleteView,
        'table': views.HtmxTableView,
        'chart': views.HtmxChartDataView,
    }
    fields = None

    enabled_filter_form_class: Optional[forms.Form] = EnabledFilterForm
    add_filter_form_class: Optional[forms.Form] = AddFilterForm
    remove_filter_form_class: Optional[forms.Form] = RemoveFilterForm

    # For Chart
    chart_class = MixedChart
    label_field = None
    data_fields = None

    @classmethod
    def get_urls(cls):  # @NoSelf
        return [view.url_path for view in cls.get_views()]

    @classmethod
    def get_url_names(cls):
        return {code: f'{cls.namespace}:{cls.node_id}-{code}'
                for code in cls.url_paths.keys()}

    @classmethod
    def get_model_fields(cls):
        return [field.name for field in cls.model._meta.fields]

    @classmethod
    def get_fields(cls):
        return getattr(cls, 'fields') or cls.get_model_fields()

    @classmethod
    def get_views(cls):
        views = [cls.get_view(code, view_cls) 
                 for code, view_cls in cls.view_classes.items()]
        return views

    @classmethod
    def get_view(cls, code, view_class):
        view_kwargs = {'viewset': cls}
        new_view_class = type(view_class.__name__, (view_class,), view_kwargs)

        url_path = cls.url_paths[code]
        url_name = cls.url_names[code].split(':')[-1]
        setattr(
            new_view_class,
            'url_path',
            path(url_path, new_view_class.as_view(), name=url_name),
        )
        return new_view_class


class HtmxModelViewSet(HtmxViewSet):
    pass


def modelviewset_factory(model=None, queryset=None, **kwargs):
    cls = kwargs.get('viewset', HtmxModelViewSet)
    assert model or isinstance(queryset, QuerySet)
    model = model or queryset.model
    queryset = queryset if isinstance(queryset, QuerySet) \
        else model._default_manager.all()

    kwargs.update({
        'model': model,
        'queryset': queryset,
        'node_id': kwargs.get('node_id', model._meta.model_name),
        'namespace': kwargs.get('namespace', model.__module__.split('.')[0]),
    })
    cls = type(cls.__name__, (cls,), kwargs)
    setattr(cls, 'url_names', cls.get_url_names())
    setattr(cls, 'urls', cls.get_urls())
    setattr(cls, 'fields', cls.get_fields())
    return cls
