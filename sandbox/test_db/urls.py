from django.urls.conf import include, path
from .views import MainViewSet


urlpatterns = [
    path('main/', include(MainViewSet.urls)),
]
