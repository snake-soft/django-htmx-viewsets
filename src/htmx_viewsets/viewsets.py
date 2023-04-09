from collections import OrderedDict
from copy import copy
from abc import ABC
from typing import Iterable, Optional

from django.urls.conf import path
from django.db.models.query import QuerySet
from django import forms
from django.db.models.aggregates import Count, Avg, Sum, Min, Max, Variance,\
    StdDev
from django.db.models.functions.datetime import TruncYear, TruncMonth,\
    TruncWeek, TruncQuarter, TruncDay, TruncHour, TruncMinute, TruncSecond
from django.db.models.fields import DateTimeField, DateField, TimeField,\
    IntegerField, PositiveBigIntegerField, PositiveIntegerField,\
    PositiveSmallIntegerField, SmallIntegerField, BigIntegerField,\
    DecimalField, FloatField

from .forms import (FilterForm, AddFilterForm, RemoveFilterForm,
                    GroupByForm)
from .fields import ViewsetModelField
from .table import Table
from .chart import MixedChart
from . import views
from django.db.models.expressions import Ref


ADDITIONAL_LOOKUPS = {
    DateTimeField: {
        'trunc_year':       TruncYear,
        'trunc_month':      TruncMonth,
        'trunc_week':       TruncWeek,
        'trunc_quarter':    TruncQuarter,
        'trunc_day':        TruncDay,
        'trunc_hour':       TruncHour,
        'trunc_minute':     TruncMinute,
        'trunc_second':     TruncSecond,
    },
    DateField: {
        'trunc_year':       TruncYear,
        'trunc_month':      TruncMonth,
        'trunc_week':       TruncWeek,
        'trunc_quarter':    TruncQuarter,
    },
    TimeField: {
        'trunc_hour':       TruncHour,
        'trunc_minute':     TruncMinute,
        'trunc_second':     TruncSecond,
    },
}


NUMBER_AGGREGATES = {
    'count':    Count,
    'avg':      Avg,
    'sum':      Sum,
    'min':      Min,
    'max':      Max,
    'variance': Variance,
    'stddev':   StdDev,
}

AGGREGATES = {
    IntegerField: NUMBER_AGGREGATES,
    PositiveBigIntegerField: NUMBER_AGGREGATES,
    PositiveIntegerField: NUMBER_AGGREGATES,
    PositiveSmallIntegerField: NUMBER_AGGREGATES,
    SmallIntegerField: NUMBER_AGGREGATES,
    BigIntegerField: NUMBER_AGGREGATES,
    DecimalField: NUMBER_AGGREGATES,
    FloatField: NUMBER_AGGREGATES,
}


class HtmxViewSetBase(ABC):
    # Required:
    node_id:        str
    urls            : Iterable

    # Optional:
    master          : Optional = None
    base_template   : Optional[str] = 'htmx_viewsets/full.html'
    charts          : Iterable = []

    @classmethod
    def get_urls(cls):  # @NoSelf
        return ([view.url_path for view in cls.get_views()], cls.namespace)

    @classmethod
    def get_url_names(cls):
        return {code: f'{cls.namespace}:{cls.node_id}-{code}'
                for code in cls.url_paths.keys()}

    @classmethod
    def get_views(cls):
        views = [cls.get_view(code, view_cls) 
                 for code, view_cls in cls.view_classes.items()]
        return views

    @classmethod
    def get_view(cls, code, view_class):
        view_kwargs = {'viewset_class': cls}
        new_view_class = type(view_class.__name__, (view_class,), view_kwargs)

        url_path = cls.url_paths[code]
        url_name = cls.url_names[code].split(':')[-1]
        setattr(
            new_view_class,
            'url_path',
            path(url_path, new_view_class.as_view(), name=url_name),
        )
        return new_view_class


class HtmxViewSet(HtmxViewSetBase):
    pass


class HtmxModelViewSet(HtmxViewSet):
    full_template_name = 'htmx_viewsets/full.html'
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
    additional_lookups = ADDITIONAL_LOOKUPS
    default_aggregates = AGGREGATES
    field_class = ViewsetModelField

    filter_form_class: Optional[forms.Form] = FilterForm
    add_filter_form_class: Optional[forms.Form] = AddFilterForm
    remove_filter_form_class: Optional[forms.Form] = RemoveFilterForm
    group_by_form_class: forms.Form = GroupByForm

    # For Chart
    table_class = Table
    chart_class = MixedChart

    fields = True or []
    label_field = None
    data_fields = None

    base_queryset: QuerySet
    prefetch_related: Iterable[str] = None
    select_related: Iterable[str] = None

    def __init__(self, request):
        self.request = request
        self.register_lookups()

        # Build forms from annotated QuerySet
        self.add_filter_form = self.add_filter_form_class(
            request, self.get_lookups(self.base_queryset))

        self.remove_filter_form = self.remove_filter_form_class(
            request, self.get_lookups(self.base_queryset))

        self.filter_form = self.filter_form_class(
            request, self.get_lookups(self.base_queryset))

        self.group_by_form = self.group_by_form_class(
            request, self.get_group_by_lookups(self.base_queryset))

        qs = self.get_queryset()
        self.viewset_fields = self.get_fields(qs)
        self.chart = self.get_chart(qs, self.viewset_fields)
        self.table = self.get_table(qs, self.viewset_fields)

    def annotate_aggregates(self, qs):
        for field in qs.query.get_meta().fields:
            aggregates = self.default_aggregates.get(field.__class__, {})
            for name, func in aggregates.items():
                qs = qs.annotate(**{f'{field.name}__{name}': func(field.name)})
        return qs

    def get_lookups(self, qs, only_groupable=False):
        viewset_fields = self.get_fields(qs)
        lookups = []
        for field in viewset_fields:
            lookups += field.get_lookups(only_groupable=only_groupable)
        return lookups

    def get_group_by_lookups(self, qs):
        return self.get_lookups(qs, only_groupable=True)

    def register_lookups(self):
        for field_cls, lookups in self.additional_lookups.items():
            for expression, func in lookups.items():
                field_cls.register_lookup(func, lookup_name=expression)

    def get_queryset(self):
        # Prepare QuerySet
        qs = self.base_queryset
        if self.prefetch_related is not None:
            qs = qs.prefetch_related(*self.prefetch_related)
        if self.select_related is not None:
            qs = qs.select_related(*self.select_related)

        # Filter QuerySet
        if self.filter_form.is_valid():
            qs = self.filter_form.filter_qs(qs)

        # Group QuerySet
        if self.group_by_form.is_valid() \
                and self.group_by_form.cleaned_data.get('group_by', None):
            qs = self.group_by_form.group_qs_by(qs)
            qs = self.annotate_aggregates(qs)
        return qs


    def get_context_data(self):
        qs = self.get_queryset()
        ctx = {
            'fields': self.get_fields(qs),
            'target_url': self.request.path,
            'create_url': self.url_names.get('create', None),
            'verbose_name': self.model._meta.verbose_name,
            'verbose_name_plural': self.model._meta.verbose_name_plural,
            'dispatch_template': f'htmx_viewsets/partial.html,{self.full_template_name}',

            'node_id': self.node_id,
            'chart': self.get_chart(qs, self.get_fields(qs)),
            'add_filter_form': self.add_filter_form,
            'remove_filter_form': self.remove_filter_form,
            'enabled_filter_form': self.filter_form,
            'group_by_form': self.group_by_form,
            'get_kwargs': self.request.GET.urlencode(),
            **self.table.get_context_data(),
        }
        return ctx

    def get_fields(self, qs):
        if qs.query.group_by:
            fields = [
                *self.get_group_by_fields(qs),
                *self.get_aggregate_fields(qs),
            ]
        else:
            fields = [
                *self.get_annotated_fields(qs),
                *self.get_model_fields(qs),
            ]
        if isinstance(self.fields, list):
            fields = [field for field in fields if field.name in self.fields]
        return fields

    def get_group_by_fields(self, qs):
        fields = OrderedDict()
        if qs.query.group_by == True:
            raise
        for expression in qs.query.group_by:
            field = copy(expression.output_field)
            name = self.group_by_form.cleaned_data['group_by']
            setattr(field, 'name', name)
            fields[name] = self.field_class(field, qs)
        return [*fields.values()]

    def get_aggregate_fields(self, qs):
        fields = OrderedDict()
        for name, annotation in qs.query.annotations.items():
            if annotation.contains_aggregate:
                field = copy(annotation.output_field)
                field.name = name
                fields[name] = self.field_class(field, qs)
        return [*fields.values()]

    def get_model_fields(self, qs):
        model_fields = qs.query.get_meta().fields
        fields = (self.field_class(field, qs) for field in model_fields)
        return fields

    def get_annotated_fields(self, qs):
        fields = OrderedDict()
        for name, field in qs.query.annotations.items():
            field = copy(field.output_field)
            field.name = name
            fields[name] = self.field_class(field, qs)
        return fields

    def get_chart(self, qs, fields):
        if self.chart_class:
            chart_id = f'chart_{self.node_id}'
            return self.chart_class(qs, fields, chart_id, self.url_names)
        return None

    def get_table(self, qs, fields):
        table_id = f'{self.node_id}-table'
        return self.table_class(
            self.request, qs, fields, table_id, self.url_names)


def modelviewset_factory(model=None, queryset=None, **kwargs):
    cls = kwargs.get('viewset', HtmxModelViewSet)
    assert model or isinstance(queryset, QuerySet)
    model = model or queryset.model
    if not isinstance(queryset, QuerySet):
        queryset = model._default_manager.all()
    kwargs.update({
        'model': model,
        'base_queryset': queryset,
        'node_id': model._meta.model_name,
    })
    if 'namespace' not in kwargs:
        kwargs['namespace'] = f'{model._meta.model_name}_viewset'
    kwargs.update(kwargs)
    cls = type(cls.__name__, (cls,), kwargs)
    setattr(cls, 'url_names', cls.get_url_names())
    setattr(cls, 'urls', cls.get_urls())
    return cls
