from abc import ABC, abstractmethod
from typing import Iterable, Optional
from django.urls.conf import path
from django.db import models
from django.utils.functional import classproperty
from htmx_viewsets.master import HtmxViewsetsMaster
from . import views


class HtmxViewSetBase(ABC):
    # Required:
    node_id:        str

    # Optional:
    master = None
    base_template:  Optional[str] = 'htmx_viewsets/full.html'
    urls:           Iterable

    @classmethod
    @abstractmethod
    def get_url_names(cls):
        pass

    @classmethod
    @abstractmethod
    def get_fields(cls, code):
        pass

    @classmethod
    @abstractmethod
    def get_view_kwargs(cls, code):
        pass

    @classmethod
    @abstractmethod
    def get_view(cls, code):
        pass

    @classmethod
    @abstractmethod
    def get_views(cls):
        pass


class HtmxViewSet(HtmxViewSetBase):
    """
    Currently there is no standalone ViewSet but there might be one
    """
    @classproperty
    def urls(cls):  # @NoSelf
        return [view.url_path for view in cls.get_views()]


class HtmxModelViewSet(HtmxViewSet):
    # Required:
    model:          models.Model

    # Optional:
    namespace:      Optional[str]     = None
    url_codes:      Iterable[str]     = ['list', 'detail', 'create', 'update', 
                                         'delete', 'table']
    url_paths = {
        'list': '',
        'detail': '<int:pk>/',
        'create': 'create/',
        'update': '<int:pk>/update/',
        'delete': '<int:pk>/delete/',
        'table': 'table/',
    }
    view_classes = {
        'list': views.HtmxListView,
        'detail': views.HtmxDetailView,
        'create': views.HtmxCreateView,
        'update': views.HtmxUpdateView,
        'delete': views.HtmxDeleteView,
        'table': views.HtmxTableView,
    }
    master = None

    @classmethod
    def get_url_names(cls):
        model_name = cls.model._meta.model_name
        namespace = cls.namespace or cls.model.__module__.split('.')[0]
        return {code: f'{namespace}:{model_name}-{code}'
                for code in cls.url_codes}

    @classmethod
    def get_fields(cls, code):
        return getattr(cls, f'{code}_fields', None) \
            or getattr(cls, 'fields', None) \
            or [field.name for field in cls.model._meta.fields]

    @classmethod
    def get_view_kwargs(cls, code):
        view_kwargs = {
            'viewset': cls,
            'model': cls.model,
            'url_names': cls.get_url_names(),
            'url_name': cls.get_url_names()[code],
            'fields': cls.get_fields(code),
            'node_id': cls.node_id,
        }
        return view_kwargs

    @classmethod
    def get_view(cls, code):
        view_class = cls.view_classes[code]
        view_kwargs = cls.get_view_kwargs(code)
        url_path = cls.url_paths[code]
        url_name = view_kwargs['url_name'].split(':')[-1]

        new_view_class = type(view_class.__name__, (view_class,), view_kwargs)
        setattr(
            new_view_class,
            'url_path',
            path(url_path, new_view_class.as_view(), name=url_name),
        )
        return new_view_class

    @classmethod
    def get_views(cls):
        return [cls.get_view(code) for code in cls.url_codes]
