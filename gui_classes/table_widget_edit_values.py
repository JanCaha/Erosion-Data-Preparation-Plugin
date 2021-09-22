from typing import Optional, NoReturn, Tuple

from qgis.PyQt.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QFont, QRegExpValidator, QColor

from qgis.core import (QgsVectorLayer,
                       QgsVectorDataProvider,
                       QgsFeature,
                       NULL)

from ..constants import TextConstants
from ..algorithms.utils import log
from .table_widget_item import TableItemNotEditable


class TableWidgetEditNumericValues(QTableWidget):

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

        return value

    def update_values_in_layer(self, layer: QgsVectorLayer) -> NoReturn:

        log("Updating from table")

        layer_dp: QgsVectorDataProvider = layer.dataProvider()

        fi_bulk_density = layer_dp.fieldNameIndex(TextConstants.field_name_bulk_density)
        fi_corg = layer_dp.fieldNameIndex(TextConstants.field_name_corg)
        fi_init_moisture = layer_dp.fieldNameIndex(TextConstants.field_name_init_moisture)
        fi_roughness = layer_dp.fieldNameIndex(TextConstants.field_name_roughness)
        fi_canopy_cover = layer_dp.fieldNameIndex(TextConstants.field_name_canopy_cover)
        fi_skinfactor = layer_dp.fieldNameIndex(TextConstants.field_name_skinfactor)
        fi_erodibility = layer_dp.fieldNameIndex(TextConstants.field_name_erodibility)

        layer.startEditing()

        for i in range(self.rowCount()):

            log(self.item(i, 8).text())
            fid = int(self.item(i, 8).text())

            layer.changeAttributeValue(fid, fi_bulk_density, self.get_value(i, 1))
            layer.changeAttributeValue(fid, fi_corg, self.get_value(i, 2))
            layer.changeAttributeValue(fid, fi_init_moisture, self.get_value(i, 3))
            layer.changeAttributeValue(fid, fi_roughness, self.get_value(i, 4))
            layer.changeAttributeValue(fid, fi_canopy_cover, self.get_value(i, 5))
            layer.changeAttributeValue(fid, fi_skinfactor, self.get_value(i, 6))
            layer.changeAttributeValue(fid, fi_erodibility, self.get_value(i, 7))

        layer.commitChanges()

    def check_row_exist(self, feature: QgsFeature) -> Tuple[bool, Optional[int]]:

        fid = str(feature.id())
        poly_id = feature.attribute(TextConstants.field_name_poly_id)

        exists = False
        row_index = None

        for i in range(self.rowCount()):

            if fid == self.item(i, 8).text() and poly_id == self.item(i, 0).text():

                exists = True
                row_index = i

                break

        return exists, row_index

    def add_row(self, feature: QgsFeature):

        row_exist, index = self.check_row_exist(feature)

        if not row_exist:

            row_to_put = self.rowCount()
            self.insertRow(self.rowCount())

            self.setItem(row_to_put, 0, TableItemNotEditable(feature.attribute(TextConstants.field_name_poly_id)))
            self.setItem(row_to_put, 8, TableItemNotEditable(str(feature.id())))
            self.setCellWidget(row_to_put, 1, self.add_cell_value(feature.attribute(TextConstants.field_name_bulk_density)))
            self.setCellWidget(row_to_put, 2, self.add_cell_value(feature.attribute(TextConstants.field_name_corg)))
            self.setCellWidget(row_to_put, 3, self.add_cell_value(feature.attribute(TextConstants.field_name_init_moisture)))
            self.setCellWidget(row_to_put, 4, self.add_cell_value(feature.attribute(TextConstants.field_name_roughness)))
            self.setCellWidget(row_to_put, 5, self.add_cell_value(feature.attribute(TextConstants.field_name_canopy_cover)))
            self.setCellWidget(row_to_put, 6, self.add_cell_value(feature.attribute(TextConstants.field_name_skinfactor)))
            self.setCellWidget(row_to_put, 7, self.add_cell_value(feature.attribute(TextConstants.field_name_erodibility)))

        else:

            if not self.get_value(index, 1):
                self.setCellWidget(index, 1,
                                   self.add_cell_value(feature.attribute(TextConstants.field_name_bulk_density)))

            if not self.get_value(index, 2):
                self.setCellWidget(index, 2,
                                   self.add_cell_value(feature.attribute(TextConstants.field_name_corg)))

            if not self.get_value(index, 3):
                self.setCellWidget(index, 3,
                                   self.add_cell_value(feature.attribute(TextConstants.field_name_init_moisture)))

            if not self.get_value(index, 4):
                self.setCellWidget(index, 4,
                                   self.add_cell_value(feature.attribute(TextConstants.field_name_roughness)))

            if not self.get_value(index, 5):
                self.setCellWidget(index, 5,
                                   self.add_cell_value(feature.attribute(TextConstants.field_name_canopy_cover)))

            if not self.get_value(index, 6):
                self.setCellWidget(index, 6,
                                   self.add_cell_value(feature.attribute(TextConstants.field_name_skinfactor)))

            if not self.get_value(index, 7):
                self.setCellWidget(index, 7,
                                   self.add_cell_value(feature.attribute(TextConstants.field_name_erodibility)))

    def add_data(self, layer: QgsVectorLayer):

        for feature in layer.getFeatures():

            self.add_row(feature)

    def add_cell_value(self, value: Optional[float] = None) -> QLineEdit:
        cell_item = QLineEdit()
        cell_item.setPlaceholderText('No value')
        cell_item.setAlignment(QtCore.Qt.AlignRight)

        if value:
            cell_item.setText(str(value))

        validator = QRegExpValidator(QRegExp(r'^-?[0-9]+[\.,]?[0-9]{0,14}$'))
        cell_item.setValidator(validator)
        cell_item.returnPressed.connect(self.clear_focus)

        return cell_item

    def header_column(self, text: str) -> QTableWidgetItem:

        item = QTableWidgetItem(text)
        font: QFont = self.font()
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignCenter)

        return item

    def clear_focus(self):

        sender = self.sender()

        sender.clearFocus()

        row = 0
        for i in range(self.rowCount()):
            if self.cellWidget(i, self.value_col) == sender:
                row = i

        next_row = row + 1

        if next_row <= self.rowCount() - 1:
            self.cellWidget(next_row, self.value_col).setFocus()
