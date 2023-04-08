from django.urls.conf import include, path
from .views import MainViewSet


app_name = 'test_db'
urlpatterns = [
    path('main/', include(MainViewSet.urls)),
]
