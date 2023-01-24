from typing import Iterable, Optional, Dict, TYPE_CHECKING, Any, List, Callable
from collections import OrderedDict
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import models
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http.response import JsonResponse, HttpResponse
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from django.utils.functional import cached_property, classproperty
from django import forms
from django.http.request import HttpRequest
from django.db.models.query import QuerySet
from django.shortcuts import redirect, reverse
from . import Table
from .chart import ChartBase
from .table.cell import Cell
from .tab import TabManager, Tab
from django.urls.conf import path
import json
from django.db.models.aggregates import Count


if TYPE_CHECKING:
    from . import chart, viewsets


class CloseModalResponse:
    def __new__(cls) -> HttpResponse:
        msg = "<script>$(function(){$('#modal').modal('hide');})</script>"
        return HttpResponse(msg)


class RefreshDataTableResponse:
    def __new__(cls, table_id: str) -> HttpResponse:
        msg = f"""
            <script>
                $(function(){{
                    reload_table("{table_id}");
                    $('#modal').modal('hide');
                }})
            </script>
        """
        return HttpResponse(msg)


class HtmxView(ContextMixin, View):
    pass

class ViewResponse:
    def __new__(cls, view_class:View, request:HttpRequest, method:str='get',
                **kwargs:Optional[Any]) -> HttpResponse:
        view = view_class(**kwargs)
        return getattr(view, method)(request)


class HtmxModelView(HtmxView, TemplateResponseMixin, ContextMixin):
    # Is set from viewset if this is a viewset view:
    code:               str
    model: models.Model = None
    fields:             Iterable[str]
    prefetch_related:   Iterable[str] = []
    select_related:     Iterable[str] = []

    # Later: permission_required:Iterable[Permission] = []
    url_names:          Dict[str, str] = {}

    template_name:      str = 'htmx_viewsets/form.html'
    object:             models.Model
    node_id     : str
    viewset     : 'viewsets.HtmxViewSetBase'
    model: models.Model
    base_queryset: QuerySet
    queryset: QuerySet

    url_names: Dict
    url_name: str

    chart_class: ChartBase

    def __new__(cls):
        for attr in ['node_id', 'model', 'url_names', 'fields',
                     'chart_class', 'label_field',
                     'enabled_filter_form_class', 'add_filter_form_class',
                     'remove_filter_form_class']:
            setattr(cls, attr, getattr(cls.viewset, attr))
        cls.base_queryset = cls.viewset.queryset
        return ContextMixin.__new__(cls)

    def get_context_data111(self, **kwargs:Optional[Any]) -> dict:
        ctx = {
            **ContextMixin.get_context_data(self, **kwargs),
            'node_id': self.node_id,
            'chart': self.get_chart(),
            'enabled_filter_form': self.enabled_filter_form_class(self.model, self.request.GET),
            'add_filter_form': self.add_filter_form_class(self.model),
            'get_kwargs': self.request.GET.urlencode(),
        }
        return ctx

    def get_queryset(self):
        form = self.enabled_filter_form_class(self.model, self.request.GET)
        qs = self.base_queryset
        qs = qs.prefetch_related(*self.prefetch_related)
        qs = qs.select_related(*self.select_related)
        if form.is_valid():
            qs = form.filter_queryset(qs)
        else:
            raise
        return qs

    def get_success_url(self) -> Any:
        if self.object:
            self.object.refresh_from_db()
            if self.object:
                return reverse(
                    self.url_names['detail'], kwargs={'pk': self.object.pk})
        return reverse(self.url_names['list'])

    def get_context_data(self, *args:Optional[Any], **kwargs:Optional[Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update({
            'fields': self.fields,
            'target_url': self.request.path,
            'next_url': self.get_next_url(),
            'field_values': self.get_field_values(),
            'create_url': self.url_names.get('create', None),
            'verbose_name': self.model._meta.verbose_name,
            'verbose_name_plural': self.model._meta.verbose_name_plural,

            'node_id': self.node_id,
            'chart': self.get_chart(),
            'enabled_filter_form': self.enabled_filter_form_class(self.model, self.request.GET),
            'add_filter_form': self.add_filter_form_class(self.model),
            'get_kwargs': self.request.GET.urlencode(),
        })
        return ctx

    def get_field_values(self) -> Optional[OrderedDict]:
        if hasattr(self, 'object') and self.object:
            cells = [
                Cell(self.model, self.object, field) for field in self.fields]
            return OrderedDict(
                [[x.field.verbose_name, str(x)] for x in cells])

    def get_table(self) -> Table:
        return Table(self.request, self.get_queryset(), self.url_names,
                     codes=self.fields, table_id=f'{self.node_id}-table')

    def get_chart(self) -> ChartBase:
        if self.chart_class:
            return self.chart_class(self, model=self.model, queryset=self.get_queryset())
        return None

    def get_next_url(self) -> Any:
        method = self.request.method
        kwargs = getattr(self.request, method)
        return kwargs.get('next', reverse(self.url_names['list']))


class HtmxListView(HtmxModelView, ListView):
    template_name = 'htmx_viewsets/list.html'
    code = 'list'
    force_full = True
    methods = ['get', 'post']

    def post(self, request:HttpRequest, *args:Optional[Any], **kwargs:Optional[Any]):
        request_get = request.GET.copy()

        form = self.add_filter_form_class(self.model, self.request.POST)
        if form.is_valid():
            request_get.update(form.cleaned_data)
            return redirect(f'{request.path}?{request_get.urlencode()}')

        form = self.remove_filter_form_class(self.model, self.request.POST)
        if form.is_valid():
            for key in form.cleaned_data.keys():
                request_get.pop(key)
            return redirect(f'{request.path}?{request_get.urlencode()}')

        return super().post(request, *args, **kwargs)

    def get_context_data(self, *args:Optional[Any], **kwargs:Optional[Any])->Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx.pop('next_url', None)
        ctx.update(self.get_table().get_context_data())
        return ctx


class HtmxTableView(HtmxModelView, ListView):
    template_name = ''
    code = 'table'

    def get(self, request:HttpRequest, *args:Optional[Any], **kwargs:Optional[Any]) -> JsonResponse:
        return JsonResponse(self.get_table().data)


class HtmxDetailView(HtmxModelView, DetailView):
    template_name = 'htmx_viewsets/detail.html'
    code = 'detail'


class HtmxCreateView(HtmxModelView, CreateView):
    http_method_names = ['get', 'post']
    code = 'create'


class HtmxUpdateView(HtmxModelView, UpdateView):
    http_method_names = ['get', 'post']
    code = 'update'

    def get_context_data(self, *args:Optional[Any], **kwargs:Optional[Any])->Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx['form'] = self.get_form()
        ctx['next_url'] = self.get_next_url()
        ctx['object'] = self.get_object()
        return ctx


class HtmxDeleteView(HtmxModelView, DeleteView):
    template_name = 'htmx_viewsets/delete.html'
    http_method_names = ['get', 'post']
    code = 'delete'

    def get_context_data(self, *args:Optional[Any], **kwargs:Optional[Any])->Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx['next_url'] = self.get_next_url()
        return ctx

    def form_valid(self, form: forms.Form) -> HttpResponse:
        super().form_valid(form)
        if self.request.htmx:
            table = self.get_table()
            return RefreshDataTableResponse(table.table_id)
        return redirect(self.get_next_url())


class HtmxChartDataView(HtmxModelView, ListView):
    code            : str = 'chart'
    charts          : List['chart.ChartBase']
    template_name = ''

    def get(self, request:HttpRequest, *args:Optional[Any], **kwargs:Optional[Any]) -> JsonResponse:
        return JsonResponse({'data': self.get_chart().data})
