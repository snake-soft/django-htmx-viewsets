from typing import Iterable, Optional, Dict, TYPE_CHECKING, Any, List, Callable
from collections import OrderedDict
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import models
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http.response import JsonResponse, HttpResponse
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from django import forms
from django.http.request import HttpRequest
from django.db.models.query import QuerySet
from django.shortcuts import redirect, reverse
from .chart import ChartBase


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
    #url_names:          Dict[str, str] = {}

    template_name:      str = 'htmx_viewsets/form.html'
    object:             models.Model
    node_id     : str
    viewset_class     : 'viewsets.HtmxViewSetBase'
    viewset     : 'viewsets.HtmxViewSetBase'
    model: models.Model
    base_queryset: QuerySet
    queryset: QuerySet

    url_names: Dict
    url_name: str

    chart_class: ChartBase

    def __new__(cls):
        setattr(cls, 'url_names', cls.viewset_class.url_names)
        return ContextMixin.__new__(cls)

    def dispatch(self, request, *args, **kwargs):
        self.viewset = self.viewset_class(request)
        self.fields = self.get_fields()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.viewset.get_queryset()

    def get_fields(self):
        qs = self.get_queryset()
        model_fields = [field.name for field in qs.query.get_meta().fields 
                        if not field.primary_key]
        viewset_fields = [field.name for field in self.viewset.viewset_fields]
        return [model_field for model_field in model_fields 
                if model_field in viewset_fields]

    def get_success_url(self) -> Any:
        if self.object:
            self.object.refresh_from_db()
            if self.object:
                return reverse(
                    self.url_names['detail'], kwargs={'pk': self.object.pk})
        return reverse(self.url_names['list'])

    def get_context_data(self, *args:Optional[Any], **kwargs:Optional[Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update(self.viewset.get_context_data())
        ctx['field_values'] = self.get_field_values()
        ctx['next_url'] = self.get_next_url()
        return ctx

    def get_field_values(self) -> Optional[OrderedDict]:
        if hasattr(self, 'object') and self.object:
            row = self.viewset.table.get_row(self.object)
            values = [(cell.verbose_name, cell.render()) for cell in row.cells]
            return OrderedDict(values)

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

        form = self.viewset.add_filter_form
        if form.is_valid():
            request_get.update(form.cleaned_data)

        form = self.viewset.remove_filter_form
        if form.is_valid():
            for key in form.cleaned_data.keys():
                request_get.pop(key)

        form = self.viewset.group_by_form
        request_get.pop('group_by', None)
        if form.is_valid():
            request_get.update(form.cleaned_data)

        return redirect(f'{request.path}?{request_get.urlencode()}')

    def get_context_data(self, *args:Optional[Any], **kwargs:Optional[Any])->Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx.pop('next_url', None)
        return ctx


class HtmxTableView(HtmxModelView, ListView):
    template_name = ''
    code = 'table'

    def get(self, request:HttpRequest, *args:Optional[Any], **kwargs:Optional[Any]) -> JsonResponse:
        return JsonResponse(self.viewset.table.data)

    def post(self, request:HttpRequest, *args:Optional[Any], **kwargs:Optional[Any]) -> JsonResponse:
        return self.get(request, *args, **kwargs)


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
            return RefreshDataTableResponse(self.viewset.table.table_id)
        return redirect(self.get_next_url())


class HtmxChartDataView(HtmxModelView, ListView):
    code            : str = 'chart'
    charts          : List['chart.ChartBase']
    template_name = ''

    def get(self, request:HttpRequest, *args:Optional[Any], **kwargs:Optional[Any]) -> JsonResponse:
        return JsonResponse({'data': self.viewset.chart.data})
