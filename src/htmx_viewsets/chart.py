import json
import datetime
from abc import ABC
from typing import Iterable, Optional
from decimal import Decimal as D
from django.db import models
from django.utils.functional import cached_property
from django.db.models.query import QuerySet


class ChartBase(ABC):
    label_field: Optional[str] = None
    data_fields: Optional[Iterable[str]] = None
    type = None  # May be set on subclass
    options = {
        'interaction': {
            'intersect': False,
            'mode': 'index',
        },
    }
    plugins = {
        'decimation': {
            'enabled': True,
            'algorithm': 'lttb',
            'samples': 500,
        },
    }
    max_data_points = 1000

    def __init__(self, view, model=None, queryset=None, data_fields=None,
                 label_field=None, options=None, type=None):
        super().__init__()
        self.view = view
        self.chart_id = f'chart_{view.node_id}'
        self.url = view.url_names['chart']

        assert isinstance(model, models.Model) or isinstance(queryset, QuerySet)
        self.model = self.get_model(queryset=queryset, model=model)
        self.queryset = self.get_queryset(queryset=queryset, model=model)
        self.options = self.get_options(options=options)

        self.type = self.get_type(type=type)
        self.label_field = self.get_label_field(label_field=label_field)
        self.data_fields = self.get_data_fields(data_fields=data_fields)

    @cached_property
    def values_list(self):
        fields = [self.label_field, *self.data_fields]
        return [*self.queryset.values_list(*fields)]

    def get_model(self, queryset=None, model=None):
        return model or queryset.model

    def get_queryset(self, queryset=None, model=None):
        if isinstance(queryset, QuerySet):
            qs = queryset#[:100]
        else:
            qs = model.objects.all()#[:100]
        return qs[:self.max_data_points]

    def get_default_data_fields(self):
        allowed_field_types = [
            'IntegerField'
            'PositiveBigIntegerField',
            'PositiveIntegerField',
            'PositiveSmallIntegerField',
            'SmallIntegerField',
            'FloatField',
            'DecimalField',
            'BooleanField',
            'DurationField',
            'DateTimeField',
            'DateField',
        ]
        model_fields = [field.name for field in self.model._meta.fields
                        if field.get_internal_type() in allowed_field_types]
        return model_fields

    def get_data_fields(self, data_fields=None):
        if data_fields is not None:
            return data_fields
        if self.__class__.data_fields is not None:
            return self.__class__.data_fields
        return self.get_default_data_fields()

    def get_default_label_field(self):
        """
        first datetimefield or first datefield or pk
        """
        for field in self.model._meta.fields:
            if field.get_internal_type() == 'DateTimeField':
                return field.name
        for field in self.model._meta.fields:
            if field.get_internal_type() == 'DateField':
                return field.name
        import pdb; pdb.set_trace()  # <---------

    def get_label_field(self, label_field=None):
        if label_field is not None:
            return label_field
        if self.__class__.label_field is not None:
            return self.__class__.label_field
        return self.get_default_label_field()

    @property
    def config(self):
        config = {
            'type': self.type,
            'data': [],
            'options': self.options,
        }
        return config

    @property
    def config_json(self):
        return json.dumps(self.config)

    @property
    def data(self):
        data = {
            'labels': self.get_labels(),
            'datasets': self.get_datasets(),
        }
        return data

    def get_dataset_classes(self):
        default_datasets = [
            Dataset.from_field_code(self, code) for code in self.fields]
        return self.dataset_classes or default_datasets

    def get_datasets(self):
        values_list = [
            [self.clean_data(y) for y in x[1:]] 
            for x in self.values_list
        ]
        datasets = []
        fields = [self.model._meta.get_field(code) for code in self.data_fields]
        for i, code in enumerate(self.data_fields):
            data = [x[i] for x in values_list]
            label = fields[i].verbose_name or fields[i].name.title()
            datasets.append({
                'type': self.type,
                'label': label,
                'data': data,
            })
        return datasets

    def get_options(self, options=None):
        if options is not None:
            return options
        if self.__class__.options is not None:
            return self.__class__.options
        return {}

    def get_labels(self):
        labels = [str(x[0]) for x in self.values_list]
        return labels

    @staticmethod
    def clean_data(data):
        if isinstance(data, D):
            return float(data)
        if isinstance(data, datetime.timedelta):
            return data.total_seconds()
        if isinstance(data, datetime.datetime):
            return data.timestamp()
        if isinstance(data, datetime.date):
            return datetime.datetime.fromordinal(data.toordinal()).timestamp()
        if isinstance(data, datetime.time):
            return NotImplementedError
        return data

    def get_type(self, type):
        if type is not None:
            return type
        if self.__class__.type is not None:
            return self.__class__.type
        return 'line'


class MixedChart(ChartBase):
    type = None


class BarChart(ChartBase):
    type = 'bar'


class BubbleChart(ChartBase):
    type = 'bubble'


class DoughnutChart(ChartBase):
    type = 'doughnut'


class PieChart(ChartBase):
    type = 'pie'


class LineChart(ChartBase):
    type = 'line'


class PolarAreaChart(ChartBase):
    type = 'polarArea'


class RadarChart(ChartBase):
    type = 'radar'


class ScatterChart(ChartBase):
    type = 'scatter'
