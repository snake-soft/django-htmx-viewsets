from typing import Iterable, Optional, Dict, TYPE_CHECKING, Any, List, Callable
from collections import OrderedDict
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import models
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http.response import JsonResponse, HttpResponse
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from django.utils.functional import cached_property
from django import forms
from django.http.request import HttpRequest
from django.db.models.query import QuerySet
from django.shortcuts import redirect, reverse
from . import Table
from .table.cell import Cell
from .tab import TabManager, Tab


if TYPE_CHECKING:
    from .viewsets import HtmxViewSetBase


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
    node_id:    str
    url_path:   str
    viewset:    'HtmxViewSetBase'

    def __init__(self, *args:Optional[Any], **kwargs:Optional[Any]):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.viewset and self.viewset.master:
            return self.viewset.master.trigger_refresh_tabs(response)
        return response

    def get_context_data(self, **kwargs:Optional[Any]) -> dict:
        return {
            **ContextMixin.get_context_data(self, **kwargs),
            'node_id': self.node_id,
        }



class ViewResponse:
    def __new__(cls, view_class:View, request:HttpRequest, method:str='get',
                **kwargs:Optional[Any]) -> HttpResponse:
        view = view_class(**kwargs)
        return getattr(view, method)(request)


class HtmxModelView(HtmxView, TemplateResponseMixin, ContextMixin):
    # Is set from viewset if this is a viewset view:
    code:               str
    model:              models.Model
    fields:             Iterable[str]
    prefetch_related:   Iterable[str] = []
    select_related:     Iterable[str] = []

    # Later: permission_required:Iterable[Permission] = []
    url_names:          Dict[str, str] = {}

    template_name:      str = 'htmx_viewsets/form.html'
    object:             models.Model

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
        })
        return ctx

    def get_field_values(self) -> Optional[OrderedDict]:
        if hasattr(self, 'object') and self.object:
            cells = [
                Cell(self.model, self.object, field) for field in self.fields]
            return OrderedDict(
                [[x.field.verbose_name, str(x)] for x in cells])

    def get_queryset(self, *args:Optional[Any], **kwargs:Optional[Any]) -> QuerySet:
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.prefetch_related(*self.prefetch_related)
        qs = qs.select_related(*self.select_related)
        return qs  # .values(*self.field_codes)

    def get_next_url(self) -> Any:
        method = self.request.method
        kwargs = getattr(self.request, method)
        return kwargs.get('next', reverse(self.url_names['list']))


class HtmxModelTableView(HtmxModelView):
    @cached_property
    def table(self) -> Table:
        return Table(self.request, self.model, self.url_names,
                     object_list=self.get_queryset(), codes=self.fields, table_id=f'{self.node_id}-table')

    def get_context_data(self, *args:Optional[Any], **kwargs:Optional[Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update(self.table.get_context_data())
        return ctx


class HtmxListView(HtmxModelTableView, ListView):
    template_name = 'htmx_viewsets/list.html'
    code = 'list'
    force_full = True

    def get_context_data(self, *args:Optional[Any], **kwargs:Optional[Any])->Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx.pop('next_url', None)
        return ctx


class HtmxTableView(HtmxModelTableView, ListView):
    template_name = ''
    code = 'table'

    def get(self, request:HttpRequest, *args:Optional[Any], **kwargs:Optional[Any]) -> JsonResponse:
        return JsonResponse(self.table.data)


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


class HtmxDeleteView(HtmxModelTableView, DeleteView):
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
            return RefreshDataTableResponse(self.table.table_id)
        return redirect(self.get_next_url())

'''
class HtmxTabView(HtmxView):
    node_id: str
    tabs: TabManager
    url_names: Dict[str, str]
    model: models.Model
'''
