from collections import OrderedDict

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.http.request import HttpRequest


class GroupByForm(forms.Form):
    group_by = forms.ChoiceField(label=_('Gruppieren nach'), required=False)

    def __init__(self, request, lookups):
        assert isinstance(request, HttpRequest)
        super().__init__(request.GET)
        self.fields['group_by'].choices = self.get_group_by_choices(lookups)

    def get_group_by_choices(self, lookups):
        choices = [['', _('Bitte auswählen')]]
        for name, verbose_name in lookups:
            choices.append((name, verbose_name))
        return choices

    def group_qs_by(self, qs):
        group_by = self.cleaned_data.get('group_by', None)
        return qs.values(group_by).order_by(group_by)

    def clean(self):
        data = super().clean()
        if data.get('group_by', None) == '':
            del data['group_by']
        return data


class AddFilterForm(forms.Form):
    x__type = forms.ChoiceField(
        label='Art',
        choices=[
            ['f', _('Einbezogen (filter)')],
            ['e', _('Ausgenommen (exclude)')],
        ]
    )
    x__lookup = forms.ChoiceField(label=_('Eigenschaft'))
    x__value = forms.CharField(label=_('Wert'))

    def __init__(self, request, lookups):
        assert isinstance(request, HttpRequest)
        if request.method == 'POST':
            super().__init__(request.POST)
        else:
            super().__init__()
        self.fields['x__lookup'].choices = self.get_lookup_choices(lookups)

    def get_lookup_choices(self, lookups):
        lookup_choices = [('', _('Bitte auswählen'))]
        for name, verbose_name in lookups:
            lookup_choices.append((name, verbose_name))
        return lookup_choices

    def clean(self):
        data = super().clean()
        if not all((data.get('x__type', False), data.get('x__lookup', False))):
            raise ValidationError('No valid lookup')
        key = f'{data["x__type"]}__{data["x__lookup"]}'
        return {key: data["x__value"]}


class FilterLookup:
    def __init__(self, key, value):
        self.key = key
        self.name = key.split('__', 1)[1]
        self.value = value
        self.bg_class = {
            'f': 'success',
            'e': 'danger'
        }.get(key.split('__', 1)[0])


class FilterForm(forms.Form):
    method = 'GET'

    def __init__(self, request, lookups):
        super().__init__(getattr(request, self.method))
        self.fields = self.get_form_fields(lookups)
        if self.is_valid():
            self.enabled_lookups = self.get_enabled_lookups()

    def get_enabled_lookups(self):
        lookups = []
        for key, value in self.cleaned_data.items():
            lookups.append(FilterLookup(key, value))
        return lookups

    def get_form_fields(self, lookups):
        fields = OrderedDict()
        for name, verbose_name in lookups:
            field = forms.CharField()
            field.name = name
            field.verbose_name = verbose_name
            field.required = False
            fields[f'f__{name}'] = field
            fields[f'e__{name}'] = field
        return fields

    def filter_qs(self, qs):
        """
        Todo: Handle multiple filters with same lookup (OR'ed)
        """
        for key, value in self.cleaned_data.items():
            method_code, lookup = key.split('__', 1)
            method = {'f': 'filter', 'e': 'exclude'}[method_code]
            qs = getattr(qs, method)(**{lookup: value})
        return qs

    def clean(self):
        data = super().clean()
        return {key: value for key, value in data.items() if key in self.data}


class RemoveFilterForm(FilterForm):
    method = 'POST'

    def clean(self):
        data = super().clean()
        delete_fields = {}
        if data.get('delete_method_lookup', False):
            method_lookup, value = data['delete_method_lookup'].split('=')
            field = self.fields[method_lookup]
            field.validate(value)
            delete_fields[method_lookup] = value
        return delete_fields
