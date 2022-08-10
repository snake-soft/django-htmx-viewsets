from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls.conf import path
from django.db import models
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from typing import Iterable, Optional
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import JsonResponse, HttpResponse
from collections import OrderedDict
from django.urls.base import reverse
from django.contrib.auth.models import Permission
from django import forms
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from . import Table
from .table.cell import Cell


class CloseModalResponse:
    def __new__(cls):
        msg = "<script>$(function(){$('#modal').modal('hide');})</script>"
        return HttpResponse(msg)


class RefreshDataTableResponse:
    def __new__(cls):
        msg = ""
        return HttpResponse(msg)
    

class ViewResponse:
    def __new__(cls, view_class, request, method='get', **kwargs):
        view = view_class(**kwargs)
        method = getattr(view, method)
        return method(request)


class HtmxMixin(TemplateResponseMixin, ContextMixin):
    namespace: str
    permission_required:Iterable[Permission] = []
    partial_template_name: str = 'htmx_viewsets/modal/form.html'
    full_template_name: str = partial_template_name

    code: str
    create_url: str
    form_class: Optional[forms.Form] = None
    prefetch_related = []
    select_related = []

    def __init__(self, *args, **kwargs):
        self.namespace =  self.model.__module__.split('.')[0]
        self.create_url = reverse(self.namespace + ':' + self.create_url)
        assert self.create_url
        super().__init__(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update({
            'template_name': self.get_template_names(),
            'target_url': self.request.path,
            'next_url': self.request.GET.get('next', None),
            'full_template_name': self.full_template_name,
            'create_url': self.create_url,
        })
        
        print('create_url: ' + ctx['create_url'])
        return ctx

    def get_template_names(self):
        return self.partial_template_name if self.request.htmx \
            else self.full_template_name

    def form_valid(self, form):
        self.object = form.save()
        return CloseModalResponse()


class HtmxTableMixin(HtmxMixin):
    partial_template_name: str = 'htmx_viewsets/list.html'
    model: models.Model
    fields: Iterable[models.Field]
    node_id: str

    def dispatch(self, request, *args, **kwargs):
        self.fields = self.get_fields()
        self.field_codes = [field.name for field in self.fields]
        self.table = Table(request, self.get_queryset(), codes=self.field_codes)
        return super().dispatch(request, *args, **kwargs)

    def get_fields(self):
        fields = getattr(self, 'fields', self.model._meta.fields)
        if fields and isinstance(fields[0], str):
            fields = [self.model._meta.get_field(field) for field in fields]
        return fields

    def get_context_data(self, *args, **kwargs):
        ctx = {
            **super().get_context_data(*args, **kwargs),
            **self.table.get_context_data(),
            'fields': self.fields,
            'verbose_name': self.model._meta.verbose_name,
            'verbose_name_plural': self.model._meta.verbose_name_plural,
        }
        if hasattr(self, 'object'):
            cells = [Cell(self.object, field.name) for field in self.fields]
            ctx['field_values'] = OrderedDict(
                [[x.field.verbose_name, str(x)] for x in cells])
        return ctx


class HtmxListView(HtmxTableMixin, ListView):
    template_name = 'htmx_viewsets/list.html'
    code = 'list'

    def get_context_data(self, *args, **kwargs):
        return HtmxTableMixin.get_context_data(self, *args, **kwargs)


class JsonTableView(HtmxListView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(self.table.data)


class HtmxDetailView(HtmxTableMixin, DetailView):
    template_name = 'htmx_viewsets/detail.html'
    code = 'detail'


class HtmxCreateView(HtmxTableMixin, CreateView):
    code = 'create'


class HtmxUpdateView(HtmxTableMixin, UpdateView):
    code = 'update'


class HtmxDeleteView(HtmxTableMixin, DeleteView):
    code = 'delete'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return super(HtmxListView, self).get()
