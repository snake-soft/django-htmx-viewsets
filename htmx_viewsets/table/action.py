from django.utils.safestring import mark_safe
from django.urls.base import reverse


class TableRowAction:
    name = None
    url_name = None
    push_url = False

    def __init__(self, table, instance):
        self.table = table
        self.instance = instance

    def render(self, *args, **kwargs):
        next_url = self.table.list_url#self.request.path
        btn = f'''
        <button 
            type="button" class="btn btn-link" 
            hx-get="{self.get_hx_url()}?next={next_url}" 
            hx-swap="none" 
            hx-push-url="{self.get_hx_push_url()}">
                {self.name}
        </button>
        '''
        return mark_safe(btn)

    def get_hx_push_url(self):
        return 'true' if self.push_url else 'false'

    def get_hx_url(self):
        model_name = self.instance.__class__._meta.model_name
        namespace = self.instance.__class__._meta.app_label
        return reverse(
            f'{namespace}:{model_name}-{self.code}', kwargs={
                'pk': self.instance.pk
            }
        )
        


class DetailRowAction(TableRowAction):
    code = 'detail'
    name = '<i class="fa-solid fa-magnifying-glass text-primary"></i>'
    push_url = True


class EditRowAction(TableRowAction):
    code = 'update'
    name = '<i class="fa-solid fa-pen-to-square text-secondary"></i>'


class DeleteRowAction(TableRowAction):
    code = 'delete'
    name = '<i class="fa-solid fa-trash text-danger"></i>'

    def render(self, *args, **kwargs):
        next_url = self.table.list_url#self.request.path
        btn = f'''
        <button 
            type="button" class="btn btn-link" 
            hx-delete="{self.get_hx_url()}?next={next_url}" 
            hx-swap="none" 
            hx-push-url="{self.get_hx_push_url()}"
            hx-confirm="Are you sure?">
                {self.name}
        </button>
        '''
        return mark_safe(btn)
