    
=====================
django-htmx-viewsets
=====================

Viewsets for Django using HTMX and DataTables


Features
--------

* Categorize pages
* Original Django flatpages are not touched
* Priorize the pages
* Categorize the pages
* Admin loads the enhanced model instead of the flatpages


Installation
------------

Install using pip:

.. code-block:: bash

	pip install django-advanced-pages


You need to load both, advanced and original pages because this package uses onetoone field to enhance the original Django Flatpages app:

.. code-block:: python

   # settings.py
   INSTALLED_APPS = [
       # ...
       'django.contrib.flatpages',
       'pages.apps.PagesConfig',
       # ...
   ]


You can pass the pages to the template like this:

.. code-block:: python

   from pages.models import Page, Category
   'pages': {
      'company': Page.objects.filter(category=Category.COMPANY),
      'legal': Page.objects.filter(category=Category.LEGAL),
   },
