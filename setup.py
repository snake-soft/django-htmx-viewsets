#!/usr/bin/env python
import sys
from setuptools import find_packages, setup


install_requires = [
    'django>=3.0,<5.0',
]


tests_require = [
    'django>=3.0,<5.0',
]


setup(
    name='django-htmx-viewsets',
    #version=__version__,
    author="Snake-Soft",
    author_email="info@snake-soft.com",
    description="Viewsets for Django using HTMX, Chartjs and DataTables",
    long_description=open('README.rst').read(),
    license='GPL3',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
)
