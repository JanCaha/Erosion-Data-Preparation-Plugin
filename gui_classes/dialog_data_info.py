from typing import List, Dict
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from ..constants import TextConstants
from ..algorithms.utils import log


class DialogDataInfo(QDialog):

    label_data_quality: QLabel
    label_data_sources: QLabel
    label_histogram: QLabel

    label_data_quality_data: QLabel
    label_data_sources_data: QLabel

    def __init__(self,
                 title: List[str],
                 data: List[float],
                 sources: Dict[str, int],
                 data_quality: Dict[str, int],
                 parent=None):

        super().__init__(parent)

        ui_file = Path(__file__).parent.parent / "ui" / "data_overview.ui"

        uic.loadUi(ui_file.absolute().as_posix(), self)

        self.setWindowTitle(self.create_title_string(title))

        self.label_data_sources.setText(TextConstants.dialog_info_label_data_sources)
        self.label_data_quality.setText(TextConstants.dialog_info_label_data_quality)
        self.label_histogram.setText(TextConstants.dialog_info_label_histogram)

        self.label_data_sources_data.setText(self.create_sources_string(sources))

        self.label_data_quality_data.setText(self.create_data_quality_string(data_quality))

        self.create_histogram(data)

    def create_title_string(self, title: List[str]) -> str:
        return " - ".join(title)

    def create_sources_string(self, sources: Dict[str, int]) -> str:

        sources_string = ""

        for key in sources.keys():

            sources_string += f"{key}\n\t{sources[key]} {TextConstants.dialog_info_recods}\n"

        return sources_string

    def create_data_quality_string(self, data_quality: Dict[str, int]) -> str:

        data_quality_string = ""

        for key in data_quality.keys():
            data_quality_string += f"{key} - {data_quality[key]}\n"

        return data_quality_string

    def create_histogram(self, data: List[float]):

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedSize(500, 250)

        self.layout().addWidget(self.canvas)

        self.figure.clear()

        ax = self.figure.add_subplot(111)

        # https://matplotlib.org/stable/api/axes_api.html

        ax.hist(data, bins=50, color="orange")
        # ax.set_xlabel('Landuse type')
        # ax.set_ylabel('Frequency')
        # ax.set_title('Histogram of landuses - resting points (Distance below mean-variance)')

        if 1 == len(set(data)):
            ax.set_xlim(data[0] - data[0] * 0.1, data[0] + data[0] * 0.1)

        self.canvas.draw()
