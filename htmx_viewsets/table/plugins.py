from .cell import Cell
from .column import Column


__all__ = ['FieldsPlugin']


class FieldsPlugin:
    cell_class = Cell

    def __init__(self, model, codes):
        self.model = model
        self.columns = self.get_columns(codes)

    def get_columns(self, codes):
        return [Column(self.model, code) for code in codes]
