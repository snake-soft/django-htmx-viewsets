from django.utils.safestring import mark_safe
from django.urls.base import reverse


class TableRowAction:
    name = None
    url_name = None
    push_url = False

    def __init__(self, row, instance, url_names):
        self.row = row
        self.instance = instance
        self.url_names = url_names

    def render(self, *args, **kwargs):
        btn = f'''
        <a 
            class="btn btn-link" 
            href="{self.get_href()}" 
            hx-get="{self.get_hx_url()}" 
            hx-swap="none" 
            hx-push-url="{self.get_hx_push_url()}">
                {self.name}
        </a>
        '''
        return mark_safe(btn)

    def get_href(self):
        return f'{self.get_hx_url()}?next={reverse(self.url_names["list"])}'

    def get_hx_push_url(self):
        return 'true' if self.push_url else 'false'

    def get_hx_url(self):
        url_name = self.url_names.get(self.code, None)
        return reverse(url_name, kwargs={'pk': self.instance.pk})
        
        url_name = self.url_names.get('list', None)
        if url_name:
            return reverse(url_name)
        return None


class DetailRowAction(TableRowAction):
    code = 'detail'
    name = '<i class="fa-solid fa-magnifying-glass text-primary"></i>'


class EditRowAction(TableRowAction):
    code = 'update'
    name = '<i class="fa-solid fa-pen-to-square text-secondary"></i>'


class DeleteRowAction(TableRowAction):
    code = 'delete'
    name = '<i class="fa-solid fa-trash text-danger"></i>'

    def render11(self, *args, **kwargs):
        btn = f'''
        <button 
            type="button" class="btn btn-link" 
            hx-delete="{self.get_hx_url()}?next={reverse(self.url_names['list'])}" 
            hx-push-url="{self.get_hx_push_url()}"
            hx-confirm="Are you sure?">
                {self.name}
        </button>
        '''
        return mark_safe(btn)
