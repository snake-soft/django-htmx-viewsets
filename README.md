[![Django CI](https://github.com/snake-soft/django-htmx-viewsets/actions/workflows/django.yml/badge.svg)](https://github.com/snake-soft/django-htmx-viewsets/actions/workflows/django.yml)
[![codecov](https://codecov.io/gh/snake-soft/django-htmx-viewsets/branch/master/graph/badge.svg?token=Tyfji4Pe6Q)](https://codecov.io/gh/snake-soft/django-htmx-viewsets)
[![Maintainability](https://api.codeclimate.com/v1/badges/bf8a8ff519a38147e922/maintainability)](https://codeclimate.com/github/snake-soft/django-htmx-viewsets/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/bf8a8ff519a38147e922/test_coverage)](https://codeclimate.com/github/snake-soft/django-htmx-viewsets/test_coverage)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


django-htmx-viewsets
========================
Viewsets for Django using HTMX and DataTables.
Currently in early state.


Built with
------------------------
+ [htmx](https://htmx.org/)
+ [chart.js](https://www.chartjs.org/)
+ [jQuery](https://jquery.com/)
+ [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
+ [Datatables](https://datatables.net/)
+ [Select2](https://select2.org/)
+ [Font Awesome](https://fontawesome.com/)


Description
------------------------
When working with Django REST framework you will stumble upon so called ViewSets.
They allow you to combine a set of related Views without repeating yourself.
This aproach has no counterpart in Django itself.

Therefore I created this package.

It comes to its full power in projects where you have to create basic CRUD with listing and chart for many models.
Eg. you can use it for building a powerful statistics page for online shops.


Features
------------------------
+ Create a viewset with one line
+ Dynamic loading of DetailView, UpdateView, CreateView and DeleteView
+ Urls are auto created
+ Queryset group by, filter and exclude by all possible date and time transform lookups
+ Auto create mixed chart with AJAX loading
+ Auto create table with AJAX loading
+ Customizable architecture[^1]

[^1]: Things may change while in early state (<1.0.0)


Demo
------------------------
[Live demo](https://www.snake-soft.com/django-htmx-viewsets/)


Screenshot
------------------------
![django-htmx-viewsets_screenshot1](https://raw.githubusercontent.com/snake-soft/django-htmx-viewsets/master/docs/screenshot1.png)

Quick-Start
========================

Installation
------------------------
```
pip install django-htmx-viewsets
```

views.py
------------------------
Create a ModelViewset by passing the model
```python
MainViewSet = modelviewset_factory(model=Main)
```
or a queryset
```python
MainViewSet = modelviewset_factory(queryset=Main.objects.all(), permissions=[])
# Remove permissions kwarg if you want to use django default model permissions for the views.
```


urls.py
------------------------
```python
urlpatterns = [
    path('main/', include(MainViewSet.urls)),
]
```


Settings
------------------------
```python
MIDDLEWARE += ['django_htmx.middleware.HtmxMiddleware']
INSTALLED_APPS += ['django_htmx', 'htmx_viewsets']
```


Template
------------------------
Project contains a full template.
If you want to use your own template, you can overwrite the template (htmx_viewsets/full.html) or pass the full_template_name as kwarg to modelviewset_factory.
The template should contain the following tags and blocks:

```html
{% load htmx_viewsets %}
<html>
  <head>
    {% htmx_viewsets_static_all %}
  </head>
  <body>
    <div class="container">
      {% block main %}{% endblock main %}
      {% htmx_viewsets_fixed_content %}
    </div>
  </body>
</html>
```
htmx_viewsets_static_all can be splitted by using htmx_viewsets_static_js and htmx_viewsets_static_css.

htmx_viewsets_fixed_content can be splitted by using htmx_viewsets_modal and htmx_viewsets_messages.


Development
========================

Sandbox
------------------------
The sandbox has multiple models containing almost all oob Django fields and relations.
Currently only BinaryField, FileField, FilePathField and ImageField are missing.

```
git clone git@github.com:snake-soft/django-htmx-viewsets.git
cd django-htmx-viewsets
virtualenv -p python3 venv
source venv/bin/activate
pip install -e .[test]
./manage.py migrate
./manage.py runserver_plus
# To create maaaany objects:
./manage.py create_objects -w
```

The purpose of the 'create_objects'-command is to create a huge database to analyze the behavior in scenarios with a bigger amount of data.
To create a smaller db use the command like this:

```
./manage.py create_objects -c 100 -w
# Create 100 of every object (Main, Parent, Child, Attribute and AttributeValues).
# w is needed when using custom parameters to confirm writing to db.
```

Status
------------------------
This project is currently under heavy development but the main architecture is finished.
All described interfaces (-> Quick-Start) will be kept but there may be changes under the hood.

Versioning
------------------------
We use [semver](https://semver.org/).

+ Major: Huge steps to make incompatible changes that change the documented behaviour 
+ Minor: Changes in undocumented functionalities
+ Micro: Patches to fix smaller problems without changing interfaces

Code Style
------------------------
+ [PEP-8](https://peps.python.org/pep-0008/)
+ Default line length of 80 chars

Contribution
------------------------
Feel free to create a [pull request](https://github.com/snake-soft/django-htmx-viewsets/pulls).
If you find any errors, please [create an issue here](https://github.com/snake-soft/django-htmx-viewsets/issues) with all neccessary details.
