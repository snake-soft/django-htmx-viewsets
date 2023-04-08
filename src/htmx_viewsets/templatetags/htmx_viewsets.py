from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe


register = template.Library()


STATICFILES = {
    'jquery': ['jquery/3.6.4/jquery-3.6.4.min.js'],
    'bootstrap': ['bootstrap/5.2.3/bootstrap.min.js',
                  'bootstrap/5.2.3/bootstrap.min.css'],
    'htmx': ['htmx/1.8.6/htmx.min.js'],
    'datatables': ['datatables/1.13.1/datatables.min.js',
                   'datatables/1.13.1/datatables.min.css'],
    'font-awesome': ['font-awesome/6.4.0/css/all.min.css'],
    'select2': ['select2/4.1.0-rc.0/select2.min.js',
                'select2/4.1.0-rc.0/select2.min.css'],
}


def get_static(file_type):
    static_names = []
    for filelist in STATICFILES.values():
        for filename in filelist:
            if filename.endswith(file_type):
                static_names.append(static(filename))
    return static_names


@register.simple_tag(name='htmx_viewsets_static_js')
def static_js():
    return mark_safe('\n'.join([f'<script src="{file}"></script>'
                      for file in get_static('js')]))


@register.simple_tag(name='htmx_viewsets_static_css')
def static_css():
    return mark_safe('\n'.join([f'<link rel="stylesheet" href="{file}" />'
                      for file in get_static('css')]))


@register.simple_tag(name='htmx_viewsets_static_all')
def static_all():
    return mark_safe(f'{static_js()}\n{static_css()}')


@register.simple_tag(name='htmx_viewsets_modal')
def modal():
    return mark_safe("""
    <div id="modal" class="modal" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-dialog-centered modal-lg" role="document">
        <div id="modal-content" class="modal-content">
          <div class="spinner-border mx-auto my-5" role="status">
            <span class="sr-only">Loading...</span>
          </div>
        </div>
      </div>
    </div>
    """)


@register.simple_tag(name='htmx_viewsets_messages')
def messages():
    return mark_safe("""
    <div class="container-fluid position-fixed" style="z-index: 10000000;bottom:0;left:0;visibility:hidden;">
      <div class="row">
        <div id="messages" style="visibility: visible;"></div>
      </div>
    </div>
    """)
    

@register.simple_tag(name='htmx_viewsets_fixed_content')
def fixed_content():
    return mark_safe(f'{modal()}\n{messages()}')
