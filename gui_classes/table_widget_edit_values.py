from typing import Optional, NoReturn, Tuple

from qgis.PyQt.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QRegExp, QObject
from qgis.PyQt.QtGui import QFont, QRegExpValidator, QColor

from qgis.core import (QgsVectorLayer,
                       QgsVectorDataProvider,
                       QgsFeature)

from ..constants import TextConstants
from ..algorithms.utils import log
from .table_widget_item import TableItemNotEditable

ROUND_PLACES = 4


class TableWidgetEditNumericValues(QTableWidget):

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
                         TextConstants.field_name_fid: 8}

    cols = list(fields_names_cols.keys())

    def __init__(self,
                 parent=None):

        QTableWidget.__init__(self, parent)

        self.any_cell_empty = False

        self.setSortingEnabled(True)

        self.setColumnCount(9)

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

        if value:
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

    def get_row_column(self, sender: QObject) -> tuple[int, int]:

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

    def change_data_value(self):

        row, column = self.get_row_column(self.sender())

        self.change_data(int(self.item(row, self.fields_names_cols[TextConstants.field_name_fid]).text()),
                         self.cols[column],
                         self.get_value(row, column))

    def change_data(self, feature_fid: int, column: str, value: float):

        self.data_layer.startEditing()

        field_index = self.data_layer_dp.fieldNameIndex(column)

        feature = self.data_layer.getFeature(feature_fid)

        feature.setAttribute(field_index, value)

        self.data_layer.updateFeature(feature)

        self.data_layer.commitChanges()
