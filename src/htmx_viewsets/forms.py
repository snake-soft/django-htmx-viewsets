import json
from django import forms
from django.db import models
from django.core.exceptions import ValidationError


class Lookup:
    def __init__(self, model_field, name, method_code=None):
        self.model_field = model_field
        self.method_code = method_code
        self.name = name
        self.form_field = self.get_form_field(model_field, name)# or forms.IntegerField()
        self.lookup = f'{model_field.name}__{name}'
        self.label = f'{model_field.verbose_name}: {self.lookup}'
        self.bg_class = self.get_bg_class(method_code)

    @property
    def method_lookup(self):
        if self.method_code is None:
            raise AttributeError('Method code is needed.')
        return f'{self.method_code}__{self.lookup}'

    @staticmethod
    def get_bg_class(method_code):
        return {'f': 'success', 'e': 'danger'}.get(method_code, None)

    @staticmethod
    def get_form_field_widget(model_field, widget, name):
        model_field_widget = {
            models.EmailField: forms.widgets.TextInput(),
        }
        widget = model_field_widget.get(model_field.__class__, widget)

        lookup_name_widget = {
            'isnull': forms.widgets.NullBooleanSelect(),
        }
        widget = lookup_name_widget.get(name, widget)
        return widget

    @classmethod
    def get_form_field(cls, model_field, name):
        form_field = model_field.formfield() or forms.IntegerField()
        form_field.widget = cls.get_form_field_widget(
            model_field, form_field.widget, name) 
        form_field.required = False
        form_field.label = name
        return form_field

    @staticmethod
    def get_model_fields(model):
        return model._meta.fields

    @classmethod
    def from_model_field(cls, model_field: models.Field, methods: bool=False):
        remove_str_only = [
            'iexact', 'contains', 'icontains', 'startswith', 'istartswith',
            'endswith', 'iendswith', 'regex', 'iregex']
        remove_number_only = []
        ignore_lookups = {
            models.BigAutoField: remove_str_only,
            models.CharField: remove_number_only,
            models.SlugField: remove_number_only,
            models.TextField: remove_number_only,
            models.URLField: remove_number_only,
            models.UUIDField: remove_number_only,
            models.ForeignKey: remove_str_only,
            models.BooleanField: remove_str_only,
            models.DateField: remove_str_only,
            models.DateTimeField: remove_str_only,
            models.TimeField: remove_str_only,
            models.IntegerField: remove_number_only,
            models.SmallIntegerField: remove_number_only,
            models.PositiveSmallIntegerField: remove_number_only,
            models.PositiveIntegerField: remove_number_only,
            models.PositiveBigIntegerField: remove_number_only,
            models.DecimalField: remove_number_only,
            #models.DurationField: remove_number_only,
            models.EmailField: remove_number_only,
            models.FloatField: remove_number_only,
            models.GenericIPAddressField: remove_number_only,
            models.JSONField: remove_number_only,
        }
        ignore_model_field_classes = [
            models.DurationField,
        ]
        for lookup_name in model_field.get_lookups():
            if any((
                model_field.__class__ in ignore_model_field_classes,
                model_field.null is False and lookup_name in ['isnull'],
                lookup_name in ['in', 'range'],
                lookup_name in ignore_lookups.get(model_field.__class__, []),
                )):
                continue
            if methods:
                yield cls(model_field, lookup_name, method_code='f')
                yield cls(model_field, lookup_name, method_code='e')
            else:
                yield cls(model_field, lookup_name)

    @classmethod
    def from_model(cls, model, methods=False):
        for model_field in cls.get_model_fields(model):
            for lookup in Lookup.from_model_field(model_field, methods=methods):
                yield lookup


class FilterFormBase(forms.Form):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookups = [*self.get_lookups(model, )]
        self.method_lookups = [*self.get_lookups(model, methods=True)]

    @staticmethod
    def get_lookups(model, methods=False):
        return Lookup.from_model(model, methods=methods)

    def get_lookup_choices(self):
        lookup_choices = [['', 'Bitte auswählen']]
        for lookup in self.lookups:
            lookup_choices.append([lookup.lookup, lookup.label])
        return lookup_choices


class AddFilterForm(FilterFormBase):
    x__type = forms.ChoiceField(
        label='Art',
        choices=[
            ['f', 'Einbezogen (filter)'],
            ['e', 'Ausgenommen (exclude)'],
        ]
    )
    x__lookup = forms.ChoiceField(label='Eigenschaft')
    x__argument = forms.CharField(label='Wert')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['x__lookup'].choices = self.get_lookup_choices()

    def clean(self):
        data = super().clean()
        if not all((data.get('x__type', False), data.get('x__lookup', False))):
            raise ValidationError('No valid lookup')
        key = f'{data["x__type"]}__{data["x__lookup"]}'
        return {key: data["x__argument"]}



class EnabledFilterForm(FilterFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = self.get_fields()
        self.is_valid()
        self.enabled_lookups = [*self.get_enabled_lookups()]

    @property
    def types(self):
        types = {}
        for lookup in self.lookups:
            widget = lookup.form_field.widget
            types[lookup.lookup] = widget.render('x__argument', None)
        return types

    @property
    def types_json(self):
        return json.dumps(self.types)

    def get_enabled_lookups(self):
        for key, value in self.cleaned_data.items():
            for lookup in self.method_lookups:
                if lookup.method_lookup == key:
                    setattr(lookup, 'value', value)
                    yield lookup

    def get_fields(self):
        fields = {lookup.method_lookup: lookup.form_field 
                  for lookup in self.method_lookups}
        for lookup, field in fields.items():
            setattr(field, 'enabled', self.data.get(lookup, None) is not None)
        return fields

    def filter_queryset(self, qs):
        for key, value in self.cleaned_data.items():
            method_code, lookup = key.split('__', 1)
            method = {'f': 'filter', 'e': 'exclude'}[method_code]
            qs = getattr(qs, method)(**{lookup: value})
        return qs

    def clean(self):
        return {key: value for key, value in super().clean().items() if value}


class RemoveFilterForm(EnabledFilterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        delete_fields = {}
        if self.data.get('delete_method_lookup', False):
            method_lookup, value = self.data['delete_method_lookup'].split('=')
            field = self.fields[method_lookup]
            field.validate(value)
            delete_fields[method_lookup] = value
        return delete_fields
