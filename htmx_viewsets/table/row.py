from django.shortcuts import render
from .cell import Cell


__all__ = ['Row']


class Row:
    """ this is a list of cells """
    def __init__(self, table, instance, codes, row_actions):
        self.instance = instance
        self.codes = codes
        self.row_actions = [action(table, instance) for action in row_actions]
        self.cells = self.get_cells(instance, codes)

    def get_cells(self, instance, codes):
        return [Cell(instance, code) for code in codes]

    @property
    def data(self):
        data = [str(cell) for cell in self.cells]
        if self.row_actions:
            actions = ''.join(action.render() for action in self.row_actions)
            data.append(f'<div class="btn-group">{actions}</div>')
        return data

    def __repr__(self):
        return 'Row:' + str(self)

    def __str__(self):
        return str(self.instance)
