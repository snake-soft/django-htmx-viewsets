from .cell import Cell
from .column import Column


__all__ = ['FieldsPlugin']


class FieldsPlugin:
    cell_class = Cell

    def __init__(self, model, codes):
        self.model = model
        self.columns = self.get_columns(model, codes)

    @staticmethod
    def get_columns(model, codes):
        return [Column(model, code) for code in codes]
