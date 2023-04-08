import json
import datetime
from typing import Iterable

from django.db.models.aggregates import Sum, Count, Avg, Min, Max, Variance,\
    StdDev

from .fields import ViewsetModelField


DATASET_OPTIONS = {
    Sum: {},
    Count: {},
    Avg: {},
    Min: {'hidden': True},
    Max: {'hidden': True},
    Variance: {'hidden': True},
    StdDev: {'hidden': True},
}


class Dataset(dict):
    def __init__(self, field, data):
        self.field                  = field
        self.update({
            'type': 'line',
            'label': field.verbose_name or field.name.title(),
            'data': [*data],
            'color': field.color,
            'borderColor': field.color,
            'backgroundColor': field.color,
        })


class ChartDatasets:
    dataset_options = DATASET_OPTIONS
    data_fields: Iterable[ViewsetModelField]

    @property
    def values_list(self):
        return self.get_values_list(self.queryset, self.fields)

    @property
    def data(self):
        data = {
            'labels': self.labels,
            'datasets': self.datasets,
        }
        return data

    @property
    def datasets(self):
        return [dataset for dataset in self.get_datasets()]

    def get_values_list(self, queryset, fields):
        names = [field.name for field in fields]
        return queryset.values_list(*names, named=True)

    def get_dataset(self, field):
        return Dataset(field)

    def get_datasets(self):
        for i, field in enumerate(self.data_fields):
            data = (x[i] for x in self.values_list)
            yield Dataset(field, data)

    @property
    def labels(self):
        return self.get_labels()

    def get_labels(self):
        return [str(x[0]) for x in self.values_list]


class ChartBase(ChartDatasets):
    #label_field: Optional[str] = None
    #data_fields: Optional[Iterable[str]] = None
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

    def __init__(self, queryset, fields, chart_id, url_names):
        super().__init__()
        assert fields is not None
        #self.field_names = field_names
        #self.fields = self.get_fields(queryset, field_names)
        self.fields = fields
        self.label_field = self.get_label_field()
        self.data_fields = self.get_data_fields()

        self.chart_id = chart_id
        self.url = url_names['chart']

        self.queryset = queryset[:self.max_data_points]


    @staticmethod
    def get_fields(queryset, field_names):
        return ViewsetModelField.get_queryset_fields(queryset, field_names)

    def get_label_field(self):
        return [*self.fields][0]

    def get_data_fields(self):
        data_fields = []
        allowed = ViewsetModelField.allowed_data_fields
        for field in self.fields: #.items():
            is_allowed = field.model_field.__class__ in allowed
            if is_allowed and field != self.label_field:
                data_fields.append(field)
        return data_fields

    @staticmethod
    def to_str(name, value, field):
        clean_str_func = getattr(field, 'clean_str_func', None)
        if clean_str_func is not None:
            value = clean_str_func(value)
        elif isinstance(value, datetime.datetime):
            value = value.strftime('%d.%m.%y %H:%M:%S')
        return value

    @classmethod
    def clean_row(cls, values_row, fields):
        return [cls.to_str(name, value, fields[name]) for name, value in values_row.items()]

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


    def get_options(self, options=None):
        if options is not None:
            return options
        if self.__class__.options is not None:
            return self.__class__.options
        return {}


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
