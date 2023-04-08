from django.db.models import fields


__all__ = ['Cell']


class Cell:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.instance = row.instance
        self.viewset_field = column.viewset_field
        self.model_field = column.viewset_field.model_field
        self.verbose_name = column.viewset_field.model_field.verbose_name

    def render(self):
        if isinstance(self.instance, dict):
            value = self.instance.get(self.model_field.name)
        else:
            value = getattr(self.instance, self.model_field.name)
        value = self.viewset_field.clean_value(value)

        if value is None:
            return '<i class="fa-solid fa-ban text-warning"></i>'

        if isinstance(self.model_field, fields.related.ManyToManyField):
            manager = getattr(self.instance, self.model_field.name)
            return ', '.join([str(x) for x in manager.all()])

        if isinstance(self.model_field, fields.BooleanField):
            return {
                True: '<i class="fa-solid fa-check text-success"></i>',
                False: '<i class="fa-solid fa-xmark text-danger"></i>',
                None: '<i class="fa-solid fa-question"></i>',
            }[value]
        
        max_length = 25
        value = str(value)
        if len(value) > max_length:
            try:
                value = value[:max_length] + '...'
            except TypeError:
                pass
        return f'<span class="cell">{value}</span>'


class ActionCell(Cell):
    name = ''
    verbose_name = ''

    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.actions = self.row.actions

    def render(self):
        actions = ''.join(action.render() for action in self.row.actions)
        return f'<div class="btn-group">{actions}</div>'
