[![Django CI](https://github.com/snake-soft/django-htmx-viewsets/actions/workflows/django.yml/badge.svg)](https://github.com/snake-soft/django-htmx-viewsets/actions/workflows/django.yml)]
[![codecov](https://codecov.io/gh/snake-soft/django-htmx-viewsets/branch/main/graph/badge.svg?token=Tyfji4Pe6Q)](https://codecov.io/gh/snake-soft/django-htmx-viewsets)]
[![Maintainability](https://api.codeclimate.com/v1/badges/bf8a8ff519a38147e922/maintainability)](https://codeclimate.com/github/snake-soft/django-htmx-viewsets/maintainability)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

django-htmx-viewsets
========================
Viewsets for Django using HTMX and DataTables

Built with
------------------------
+ [htmx](https://htmx.org/)
+ [chart.js](https://www.chartjs.org/)
+ [jQuery](https://jquery.com/)
+ [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
+ [Datatables](https://datatables.net/)

Description
------------------------
When working with Django REST framework you will stumble upon so called ViewSets.
They allow you to combine a set of related Views without repeating.
This aproach has no counterpart in Django itself.

Therefore I created this package.

Features
========================
+ Create a viewset with one line
+ Dynamic loading of DetailView, UpdateView, CreateView and DeleteView
+ Urls are auto created
+ Queryset group by, filter and exclude by all possible date and time transform lookups
+ Auto create mixed chart with AJAX loading
+ Auto create table with AJAX loading
+ Customizable architecture[^1]

[^1]: Things may change while in early state (<1.0.0)


Quick-Start
========================

Installation
------------------------
```
pip install django-htmx-viewset
```

views.py
------------------------
Create a ModelViewset by passing the model
```python
MainViewSet = modelviewset_factory(model=Main)
```
or a queryset
```python
MainViewSet = modelviewset_factory(queryset=Main.objects.all())
```


urls.py
------------------------

```python
app_name = 'test_db'
urlpatterns = [
    path('main/', include(MainViewSet.urls)),
]
```
