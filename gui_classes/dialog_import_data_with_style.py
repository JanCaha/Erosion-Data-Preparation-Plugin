from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel, QComboBox, QLineEdit, QTextBrowser
from qgis.PyQt.QtCore import pyqtSlot

from qgis.gui import QgsFileWidget, QgsOpacityWidget
from qgis.core import QgsRasterLayer

from ..constants import TextConstants
from ..algorithms.utils import log, add_maplayer_to_project


class DialogLoadResult(QDialog):

    mQgsFileWidget: QgsFileWidget
    comboBox_style: QComboBox

    label_style: QLabel
    label_input_data: QLabel
    label_opacity: QLabel
    label_layer_name: QLabel

    helpText: QTextBrowser

    lineEdit_layer_name: QLineEdit

    horizontalSlider_opacity: QgsOpacityWidget

    styles = {TextConstants.dialog_load_data_7_cat_tha: "7_cat_t_ha.qml",
              TextConstants.dialog_load_data_7_cat_kgm2: "7_cat_kg_m2.qml",
              TextConstants.dialog_load_data_9_cat_tha: "9_cat_t_ha.qml",
              TextConstants.dialog_load_data_9_cat_kgm2: "9_cat_kg_m2.qml"}

    def __init__(self, parent=None):

        super().__init__(parent)

        ui_file = Path(__file__).parent.parent / "ui" / "dialog_import_data.ui"

        uic.loadUi(ui_file.absolute().as_posix(), self)

        self.setWindowTitle(TextConstants.dialog_load_data_title)

        self.horizontalSlider_opacity.setOpacity(0.5)

        self.label_input_data.setText(TextConstants.dialog_load_data_layer)
        self.label_style.setText(TextConstants.dialog_load_data_style)
        self.label_opacity.setText(TextConstants.dialog_load_data_opacity)
        self.label_layer_name.setText(TextConstants.dialog_load_data_layer_name)

        help_text = TextConstants.dialog_load_data_help

        help_text = help_text.split("\n\n")
        help_text = [f"<p>{x}</p>" for x in help_text]
        help_text = "".join(help_text)

        self.helpText.document().setDefaultStyleSheet(".summary { margin-left: 10px; margin-right: 10px; }\n"
                                                      "h2 { color: #555555; padding-bottom: 15px; }\n"
                                                      "a { text - decoration: none; color: #3498db; font-weight: bold; }\n"
                                                      "p { color: #666666; }\n"
                                                      "b { color: #333333; }\n"
                                                      "dl dd { margin - bottom: 5px; }")

        self.helpText.setText(f"<h2>{TextConstants.dialog_load_data_title}</h2>{help_text}")

        self.lineEdit_layer_name.setText("")

        self.mQgsFileWidget.fileChanged.connect(self.set_folder_name_as_layer_name)

        self.mQgsFileWidget.setFilter("Sedbudget Arc/Info ASCII Grid (sedbudget.asc);;Arc/Info ASCII Grid (*.asc);;")
        # self.mQgsFileWidget.setFilter("GeoTiff files (*.tif);;All files (*.*)")

        self.comboBox_style.addItems(list(self.styles.keys()))
        self.comboBox_style.setCurrentIndex(0)

    def set_folder_name_as_layer_name(self, path: str) -> None:

        path = Path(path)

        self.lineEdit_layer_name.setText("sedbudget {}".format(path.parent.name))

    def get_qml_path(self) -> str:

        dir_qml = Path(__file__).parent.parent / "qml_files"

        file_qml = dir_qml / self.styles[self.comboBox_style.currentText()]

        return file_qml.absolute().as_posix()

    def get_opacity(self) -> float:

        return self.horizontalSlider_opacity.opacity()

    def load_result_data_with_style(self):

        file_path = self.mQgsFileWidget.filePath()

        if file_path:

            layer_name = self.lineEdit_layer_name.text()

            raster = QgsRasterLayer(file_path, layer_name)

            raster.loadNamedStyle(self.get_qml_path())

            raster.setOpacity(self.get_opacity())

            add_maplayer_to_project(raster)
