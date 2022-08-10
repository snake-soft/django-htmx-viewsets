from django.utils.translation import gettext_lazy as _
from django.apps.config import AppConfig


class HtmxViewsetsConfig(AppConfig):
    name = 'htmx_viewsets'
    verbose_name = _('HTMX Viewsets')
    namespace = 'htmx_viewsets'
