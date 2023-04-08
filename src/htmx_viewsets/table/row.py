
__all__ = ['Row']


class Row:
    """ this is a list of cells """
    def __init__(self, columns, instance, url_names, row_action_classes):
        self.instance = instance
        self.columns = columns
        self.actions = self.get_actions(row_action_classes, url_names)
        self.cells = self.get_cells(columns)

    def get_cells(self, columns):
        return [column.cell_class(self, column) for column in columns]

    def get_actions(self, action_classes, url_names):
        return [cls(self, url_names) for cls in action_classes]

    @property
    def data(self):
        return [cell.render() for cell in self.cells]

    def __repr__(self):
        return 'Row:' + str(self)

    def __str__(self):
        return str(self.instance)
