from typing import Iterable, Dict, TYPE_CHECKING
from django.db.models import Model
from .cell import Cell
from django.db.models.query import QuerySet


__all__ = ['Row']


if TYPE_CHECKING:
    from .table import Table  # @UnusedImport
    from .action import TableRowAction  # @UnusedImport
    


class Row:
    """ this is a list of cells """
    def __init__(
            self,
            table:      'Table',
            queryset:   QuerySet,
            instance:   Model,
            codes:      Iterable[str],
            row_actions:Iterable['TableRowAction'],
            url_names:  Dict[str,str]
            ) -> None:
        assert isinstance(queryset, QuerySet)
        self.table = table
        #self.model = model
        self.instance = instance
        self.codes = codes
        self.row_actions = [
            action(self, instance, url_names) for action in row_actions]
        self.cells = self.get_cells(queryset, instance, codes)

    @staticmethod
    def get_cells(model, instance, codes):
        return [Cell(model, instance, code) for code in codes]

    @staticmethod
    def get_action_cell(row_actions):
        actions = ''.join(action.render() for action in row_actions)
        return f'<div class="btn-group">{actions}</div>'

    @property
    def data(self):
        data = [str(cell) for cell in self.cells]
        if self.row_actions:
            data = [self.get_action_cell(self.row_actions), *data]
        return data

    def __repr__(self):
        return 'Row:' + str(self)

    def __str__(self):
        return str(self.instance)
