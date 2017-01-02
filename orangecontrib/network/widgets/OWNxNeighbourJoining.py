from AnyQt.QtWidgets import QLayout
from Orange.misc import DistMatrix
from Orange.widgets.gui import auto_commit, widgetBox, widgetLabel
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget
from orangecontrib.network import Graph


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

    def set_input_distances(self, distances):
        if distances is None:
            self.send(_Output.GRAPH, None)
            self.input_distances_info.setText(self._NO_INPUT_INFO_TEXT)
            return

        distances_info_text = (
            "Distance matrix with {:d} rows and {:d} columns on input."
        ).format(
            distances.shape[0],
            distances.shape[1]
        )

        self._input_distances = distances
        self.input_distances_info.setText(distances_info_text)

    def commit(self):
        # todo
        pass


if __name__ == '__main__':
    import sys
    from AnyQt.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = OWNeighbourJoining()
    widget.show()
    app.exec()
    widget.saveSettings()
