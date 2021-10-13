from typing import NoReturn
from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit, QProgressBar

from ..constants import TextConstants
from ..algorithms.utils import is_valid_path_for_file


class DialogResult(QDialog):

    label_data_exported: QLabel

    label_landuse_raster: QLabel
    label_parameter_table: QLabel
    label_lookup_table: QLabel
    label_pour_points_raster: QLabel

    lineEdit_landuse_raster: QLineEdit
    lineEdit_parameter_table: QLineEdit
    lineEdit_lookup_table: QLineEdit
    lineEdit_pour_points_raster: QLineEdit

    progressBar: QProgressBar

    def __init__(self,
                 path_landuse_raster: str,
                 path_parameter_table: str,
                 path_lookup_table: str,
                 path_pour_points_raster: str = None):

        super().__init__()

        ui_file = Path(__file__).parent.parent / "ui" / "exported_dialog.ui"

        uic.loadUi(ui_file.absolute().as_posix(), self)

        self.setWindowTitle(TextConstants.dialog_export_label_exported)

        self.label_data_exported.setText(TextConstants.dialog_export_label_exporting)

        self.label_lookup_table.setText(TextConstants.label_landuse_raster)
        self.label_parameter_table.setText(TextConstants.label_parameter_table)
        self.label_lookup_table.setText(TextConstants.label_lookup_table)

        self.set_text_for_path(self.lineEdit_landuse_raster, path_landuse_raster)
        self.set_text_for_path(self.lineEdit_parameter_table, path_parameter_table)
        self.set_text_for_path(self.lineEdit_lookup_table, path_lookup_table)
        self.set_text_for_path(self.lineEdit_pour_points_raster, path_pour_points_raster)

    @staticmethod
    def set_text_for_path(line_edit: QLineEdit,
                          path: str) -> NoReturn:

        if path is not None and path != "":

            if is_valid_path_for_file(path):
                line_edit.setText(path)
            else:
                line_edit.setText(TextConstants.dialog_export_label_not_valid_path)

        else:

            line_edit.setText(TextConstants.dialog_export_label_not_exported)

        line_edit.setEnabled(False)

    def export_finished(self):
        self.progressBar.hide()
        self.label_data_exported.setText(TextConstants.dialog_export_label_exported)

    def update_progress_bar(self, value: int):
        self.progressBar.setValue(value)

    def set_progress_bar(self, maximal_value: int):
        self.progressBar.setMaximum(maximal_value)
