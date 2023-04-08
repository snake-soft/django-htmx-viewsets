from htmx_viewsets.viewsets import modelviewset_factory
from .models import Main


MainViewSet = modelviewset_factory(model=Main)
