from htmx_viewsets.viewsets import HtmxModelViewSet
from htmx_viewsets.master import HtmxViewsetsMaster
from .models import Main, AttributeValue, Attribute
from django.utils.functional import classproperty
from typing import List
from django.urls.conf import path


class MainViewSet(HtmxModelViewSet):
    model = Main
    node_id = 'main'
    select_related = ['parent']


class AttributeValueViewSet(HtmxModelViewSet):
    model = AttributeValue
    node_id = 'attribute_value'


class AttributeViewSet(HtmxModelViewSet):
    model = Attribute
    node_id = 'attributes'


class TabView(HtmxViewsetsMaster):
    viewsets = [MainViewSet, AttributeValueViewSet, AttributeViewSet]
    node_id = 'mdsai'
    namespace = 'test_db'
