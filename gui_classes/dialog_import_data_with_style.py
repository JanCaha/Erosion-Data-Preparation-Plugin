from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel, QComboBox, QSlider

from qgis.gui import QgsFileWidget
from qgis.core import QgsRasterLayer

from ..constants import TextConstants
from ..algorithms.utils import log, add_maplayer_to_project


class DialogLoadResult(QDialog):

    mQgsFileWidget: QgsFileWidget
    comboBox_style: QComboBox

    label_style: QLabel
    label_input_data: QLabel
    label_opacity: QLabel
    horizontalSlider_opacity: QSlider

    styles = {TextConstants.dialog_load_data_7_cat_tha: "7_cat_t_ha.qml",
              TextConstants.dialog_load_data_7_cat_kgm2: "7_cat_kg_m2.qml",
              TextConstants.dialog_load_data_9_cat_tha: "9_cat_t_ha.qml",
              TextConstants.dialog_load_data_9_cat_kgm2: "9_cat_kg_m2.qml"}

    def __init__(self, parent=None):

        super().__init__(parent)

        ui_file = Path(__file__).parent.parent / "ui" / "dialog_import_data.ui"

        uic.loadUi(ui_file.absolute().as_posix(), self)

        self.setWindowTitle(TextConstants.dialog_load_data_title)

        self.label_input_data.setText(TextConstants.dialog_load_data_layer)
        self.label_style.setText(TextConstants.dialog_load_data_style)
        self.label_opacity.setText(TextConstants.dialog_load_data_opacity)

        self.mQgsFileWidget.setFilter("GeoTiff files (*.tif)")
        # self.mQgsFileWidget.setFilter("GeoTiff files (*.tif);;All files (*.*)")

        self.comboBox_style.addItems(list(self.styles.keys()))
        self.comboBox_style.setCurrentIndex(0)

    def get_qml_path(self) -> str:

        dir_qml = Path(__file__).parent.parent / "qml_files"

        file_qml = dir_qml / self.styles[self.comboBox_style.currentText()]

        return file_qml.absolute().as_posix()

    def get_opacity(self) -> float:

        return self.horizontalSlider_opacity.value() / 100

    def load_result_data_with_style(self):

        file_path = self.mQgsFileWidget.filePath()

        layer_name = Path(file_path).stem

        if file_path:

            raster = QgsRasterLayer(file_path, layer_name)

            raster.loadNamedStyle(self.get_qml_path())

            raster.setOpacity(self.get_opacity())

            add_maplayer_to_project(raster)
