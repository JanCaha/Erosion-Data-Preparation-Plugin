from typing import Optional, Tuple

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QRegExp, QObject
from qgis.PyQt.QtGui import QFont, QRegExpValidator, QColor
from qgis.PyQt.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit
from qgis.core import (QgsVectorLayer,
                       QgsVectorDataProvider,
                       QgsFeature)

from .table_widget_item import TableItemNotEditable
from ..constants import TextConstants

ROUND_PLACES = 4


class TableWidgetEditNumericValues(QTableWidget):

    COLOR_RED = QColor(255, 155, 155)
    COLOR_WHITE = QColor(255, 255, 255)

    FONT_SIZE = 15

    DEFAULT_STYLE_SHEET = f"QLineEdit{{" \
                          f"font-size: {FONT_SIZE}px; " \
                          f"background-color: {COLOR_RED.name()};" \
                          f"}}"

    data_layer: QgsVectorLayer
    data_layer: QgsVectorDataProvider

    fields_names_cols = {TextConstants.field_name_poly_id: 0,
                         TextConstants.field_name_bulk_density: 1,
                         TextConstants.field_name_corg: 2,
                         TextConstants.field_name_init_moisture: 3,
                         TextConstants.field_name_roughness: 4,
                         TextConstants.field_name_canopy_cover: 5,
                         TextConstants.field_name_skinfactor: 6,
                         TextConstants.field_name_erodibility: 7,
                         TextConstants.field_name_fid: 8,
                         TextConstants.field_name_FT: 9,
                         TextConstants.field_name_MT: 10,
                         TextConstants.field_name_GT: 11,
                         TextConstants.field_name_FU: 12,
                         TextConstants.field_name_MU: 13,
                         TextConstants.field_name_GU: 14,
                         TextConstants.field_name_FS: 15,
                         TextConstants.field_name_MS: 16,
                         TextConstants.field_name_GS: 17}

    cols = list(fields_names_cols.keys())

    def __init__(self,
                 parent=None):

        QTableWidget.__init__(self, parent)

        self.any_cell_empty = False

        self.setSortingEnabled(True)

        self.setColumnCount(18)

        self.setHorizontalHeaderItem(0, self.header_column(TextConstants.field_name_poly_id))
        self.setHorizontalHeaderItem(1, self.header_column(TextConstants.field_name_bulk_density))
        self.setHorizontalHeaderItem(2, self.header_column(TextConstants.field_name_corg))
        self.setHorizontalHeaderItem(3, self.header_column(TextConstants.field_name_init_moisture))
        self.setHorizontalHeaderItem(4, self.header_column(TextConstants.field_name_roughness))
        self.setHorizontalHeaderItem(5, self.header_column(TextConstants.field_name_canopy_cover))
        self.setHorizontalHeaderItem(6, self.header_column(TextConstants.field_name_skinfactor))
        self.setHorizontalHeaderItem(7, self.header_column(TextConstants.field_name_erodibility))
        self.setHorizontalHeaderItem(8, self.header_column(TextConstants.field_name_fid))

        self.setColumnHidden(8, True)

        self.setHorizontalHeaderItem(9, self.header_column(TextConstants.field_name_FT))
        self.setHorizontalHeaderItem(10, self.header_column(TextConstants.field_name_MT))
        self.setHorizontalHeaderItem(11, self.header_column(TextConstants.field_name_GT))
        self.setHorizontalHeaderItem(12, self.header_column(TextConstants.field_name_FU))
        self.setHorizontalHeaderItem(13, self.header_column(TextConstants.field_name_MU))
        self.setHorizontalHeaderItem(14, self.header_column(TextConstants.field_name_GU))
        self.setHorizontalHeaderItem(15, self.header_column(TextConstants.field_name_FS))
        self.setHorizontalHeaderItem(16, self.header_column(TextConstants.field_name_MS))
        self.setHorizontalHeaderItem(17, self.header_column(TextConstants.field_name_GS))

    def get_value(self, row: int, column: int) -> Optional[float]:

        value = self.cellWidget(row, column).text()

        if value == "":
            value = None

        if value:
            value = float(value.replace(",", "."))
            value = round(value, ROUND_PLACES)

        return value

    def add_row(self, feature: QgsFeature):

        row_to_put = self.rowCount()
        self.insertRow(row_to_put)

        self.setItem(row_to_put, 0, TableItemNotEditable(feature.attribute(TextConstants.field_name_poly_id)))
        self.setItem(row_to_put, 8, TableItemNotEditable(str(feature.id())))
        self.setCellWidget(row_to_put, 1, self.add_cell_value(feature.attribute(TextConstants.field_name_bulk_density)))
        self.setCellWidget(row_to_put, 2, self.add_cell_value(feature.attribute(TextConstants.field_name_corg)))
        self.setCellWidget(row_to_put, 3, self.add_cell_value(feature.attribute(TextConstants.field_name_init_moisture)))
        self.setCellWidget(row_to_put, 4, self.add_cell_value(feature.attribute(TextConstants.field_name_roughness)))
        self.setCellWidget(row_to_put, 5, self.add_cell_value(feature.attribute(TextConstants.field_name_canopy_cover)))
        self.setCellWidget(row_to_put, 6, self.add_cell_value(feature.attribute(TextConstants.field_name_skinfactor)))
        self.setCellWidget(row_to_put, 7, self.add_cell_value(feature.attribute(TextConstants.field_name_erodibility)))

        self.setCellWidget(row_to_put, 9, self.add_cell_value(feature.attribute(TextConstants.field_name_FT)))
        self.setCellWidget(row_to_put, 10, self.add_cell_value(feature.attribute(TextConstants.field_name_MT)))
        self.setCellWidget(row_to_put, 11, self.add_cell_value(feature.attribute(TextConstants.field_name_GT)))
        self.setCellWidget(row_to_put, 12, self.add_cell_value(feature.attribute(TextConstants.field_name_FU)))
        self.setCellWidget(row_to_put, 13, self.add_cell_value(feature.attribute(TextConstants.field_name_MU)))
        self.setCellWidget(row_to_put, 14, self.add_cell_value(feature.attribute(TextConstants.field_name_GU)))
        self.setCellWidget(row_to_put, 15, self.add_cell_value(feature.attribute(TextConstants.field_name_FS)))
        self.setCellWidget(row_to_put, 16, self.add_cell_value(feature.attribute(TextConstants.field_name_MS)))
        self.setCellWidget(row_to_put, 17, self.add_cell_value(feature.attribute(TextConstants.field_name_GS)))

        color = self.COLOR_WHITE

        if not self.validate_feature(feature_id=feature.id()):
            color = self.COLOR_RED

        self.change_row_color(row_to_put, color)

    def add_data(self, layer: QgsVectorLayer):

        self.data_layer = layer
        self.data_layer_dp = layer.dataProvider()

        self.clearContents()
        self.setRowCount(0)

        for feature in layer.getFeatures():

            self.add_row(feature)

    def add_cell_value(self, value: Optional[float] = None) -> QLineEdit:
        cell_item = QLineEdit()
        cell_item.setPlaceholderText('No value')
        cell_item.setAlignment(QtCore.Qt.AlignRight)
        cell_item.setStyleSheet(self.DEFAULT_STYLE_SHEET)

        if value or value == 0.0:
            cell_item.setText(str(round(value, ROUND_PLACES)))

        validator = QRegExpValidator(QRegExp(r'^-?[0-9]+[\.,]?[0-9]{0,14}$'))
        cell_item.setValidator(validator)
        cell_item.textChanged.connect(self.change_data_value)
        cell_item.returnPressed.connect(self.clear_focus)

        return cell_item

    def header_column(self, text: str) -> QTableWidgetItem:

        item = QTableWidgetItem(text)
        font: QFont = self.font()
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignCenter)

        return item

    def get_row_column(self, sender: QObject) -> Tuple[int, int]:

        row = 0
        column = 0

        for i in range(self.rowCount()):

            for j in range(self.columnCount()):

                if self.cellWidget(i, j) == sender:
                    row = i
                    column = j

        return row, column

    def clear_focus(self):

        sender = self.sender()

        row, column = self.get_row_column(self.sender())

        sender.clearFocus()

        next_column = column + 1
        next_row = row

        if next_column >= self.columnCount()-1:
            next_column = 1
            next_row = next_row + 1

        if next_row <= self.rowCount() - 1:
            self.cellWidget(next_row, next_column).setFocus()

    def validate_feature(self, feature_id: int) -> bool:

        feature = self.data_layer.getFeature(feature_id)

        value = float(feature.attribute(TextConstants.field_name_FT)) + \
                float(feature.attribute(TextConstants.field_name_MT)) + \
                float(feature.attribute(TextConstants.field_name_GT)) + \
                float(feature.attribute(TextConstants.field_name_FU)) + \
                float(feature.attribute(TextConstants.field_name_MU)) + \
                float(feature.attribute(TextConstants.field_name_GU)) + \
                float(feature.attribute(TextConstants.field_name_FS)) + \
                float(feature.attribute(TextConstants.field_name_MS)) + \
                float(feature.attribute(TextConstants.field_name_GS))

        if value == 100.0:
            return True

        return False

    def change_data_value(self):

        row, column = self.get_row_column(self.sender())

        feature_id = int(self.item(row, self.fields_names_cols[TextConstants.field_name_fid]).text())

        self.change_data(feature_id,
                         self.cols[column],
                         self.get_value(row, column))

        color = self.COLOR_WHITE

        if not self.validate_feature(feature_id=feature_id):
            color = self.COLOR_RED

        self.change_row_color(row, color)

    def change_data(self, feature_fid: int, column: str, value: float):

        self.data_layer.startEditing()

        field_index = self.data_layer_dp.fieldNameIndex(column)

        feature = self.data_layer.getFeature(feature_fid)

        feature.setAttribute(field_index, value)

        self.data_layer.updateFeature(feature)

        self.data_layer.commitChanges()

    def change_row_color(self, row: int, color: QColor):

        self.item(row, 0).setBackground(color)
        self.item(row, 8).setBackground(color)

        for i in range(self.columnCount()):
            if i != 0 and i != 8:
                # TODO font somehow changes after first edit
                self.cellWidget(row, i).setStyleSheet(f"QLineEdit{{"
                                                      f"font-size: {self.FONT_SIZE}px; "
                                                      f"background-color: {color.name()};"
                                                      f"}}")
