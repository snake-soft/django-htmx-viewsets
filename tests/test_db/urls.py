from django.urls.conf import include, path
from .views import TabView


app_name = 'test_db'
urlpatterns = [
    path('', include(TabView.urls)),
]
