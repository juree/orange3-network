from AnyQt.QtWidgets import QLayout
from Orange.data import Table, Domain, StringVariable
from Orange.misc import DistMatrix
from Orange.widgets.gui import auto_commit, widgetBox, widgetLabel
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget
from orangecontrib.network import Graph
from orangecontrib.network.neighbour_joining import NeighbourJoining

import numpy as np


class _Input:
    DISTANCES = "Distances"


class _Output:
    GRAPH = "Graph"


class OWNeighbourJoining(OWWidget):
    name = "Neighbour Joining"
    description = "Computes a phylogenetic tree from a distance matrix."
    icon = ""
    priority = 6470

    inputs = [(_Input.DISTANCES, DistMatrix, "set_input_distances")]
    outputs = [(_Output.GRAPH, Graph)]

    want_main_area = False
    _auto_apply = Setting(default=True)

    _NO_INPUT_INFO_TEXT = "No data on input."
    _EMPTY_MATRIX_INFO_TEXT = "Empty distance matrix."

    def __init__(self):
        super().__init__()
        self._input_distances = None
        self._setup_layout()

    def _setup_layout(self):
        self.controlArea.setMinimumWidth(self.controlArea.sizeHint().width())
        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        widget_box = widgetBox(self.controlArea, "Info")
        self.input_distances_info = widgetLabel(
            widget=widget_box,
            label=self._NO_INPUT_INFO_TEXT
        )

        auto_commit(
            widget=self.controlArea,
            master=self,
            value="_auto_apply",
            label="Apply",
            checkbox_label="Auto Apply",
            commit=self.commit
        )

    def set_input_distances(self, matrix):
        if matrix is None:
            self.send(_Output.GRAPH, None)
            self.input_distances_info.setText(self._NO_INPUT_INFO_TEXT)
            return
        else:
            N, _ = matrix.shape
            if N < 2:
                self.send(_Output.GRAPH, None)
                self.input_distances_info.setText(self._EMPTY_MATRIX_INFO_TEXT)
                return

        distances_info_text = (
            "Distance matrix with {:d} rows and {:d} columns on input."
        ).format(
            matrix.shape[0],
            matrix.shape[1]
        )

        self._input_distances = matrix
        self.input_distances_info.setText(distances_info_text)

    def commit(self):
        matrix = self._input_distances

        graph = Graph()
        graph.add_nodes_from(range(matrix.shape[0]))

        if matrix is not None and matrix.row_items is not None:
            if isinstance(matrix.row_items, Table):
                graph.set_items(matrix.row_items)
            else:
                data = [[str(x)] for x in matrix.row_items]
                items = Table(Domain([], metas=[StringVariable('label')]), data)
                graph.set_items(items)

        # Add (weighted) edges
        edge_list = []
        rows, cols = matrix.shape
        for i in range(rows):
            for j in range(i + 1, cols):
                edge_list.append((i, j, matrix[i, j]))

        graph.add_edges_from((u, v, {'weight': d}) for u, v, d in edge_list)

        self.send(_Output.GRAPH, graph)


if __name__ == '__main__':
    import sys
    from AnyQt.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = OWNeighbourJoining()
    widget.show()
    app.exec()
    widget.saveSettings()
