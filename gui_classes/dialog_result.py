from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit

from ..constants import TextConstants


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

    def __init__(self,
                 path_landuse_raster: str,
                 path_parameter_table: str,
                 path_lookup_table: str,
                 path_pour_points_raster: str = None):

        super().__init__()

        ui_file = Path(__file__).parent.parent / "ui" / "exported_dialog.ui"

        uic.loadUi(ui_file.absolute().as_posix(), self)

        self.setWindowTitle(TextConstants.dialog_export_label_exported)

        self.label_data_exported.setText(TextConstants.dialog_export_label_exported)

        self.label_lookup_table.setText(TextConstants.label_landuse_raster)
        self.label_parameter_table.setText(TextConstants.label_parameter_table)
        self.label_lookup_table.setText(TextConstants.label_lookup_table)

        self.lineEdit_landuse_raster.setText(path_landuse_raster)
        self.lineEdit_landuse_raster.setEnabled(False)

        self.lineEdit_parameter_table.setText(path_parameter_table)
        self.lineEdit_parameter_table.setEnabled(False)

        self.lineEdit_lookup_table.setText(path_lookup_table)
        self.lineEdit_lookup_table.setEnabled(False)

        if path_pour_points_raster is not None and path_pour_points_raster != "":
            self.lineEdit_pour_points_raster.setText(path_pour_points_raster)
        else:
            self.lineEdit_pour_points_raster.setText(TextConstants.dialog_export_label_not_exported)

        self.lineEdit_pour_points_raster.setEnabled(False)


