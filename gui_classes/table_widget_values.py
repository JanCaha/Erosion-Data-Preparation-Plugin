from typing import Dict, Any, List, Optional

from pathlib import Path

from qgis.PyQt.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QFont, QRegExpValidator

from ..constants import TextConstants
from ..classes.definition_landuse_values import LanduseValues
from .table_widget_item import TableItemNotEditable


class TableWidgetLanduseAssignedValues(QTableWidget):

    def __init__(self, parent=None, ):

        QTableWidget.__init__(self, parent)

        self.any_cell_empty = False

        self.setColumnCount(7)

        self.setHorizontalHeaderItem(0, self.header_column(TextConstants.tw_lv_col_value))
        self.setHorizontalHeaderItem(1, self.header_column(TextConstants.tw_lv_col_bulkdensity))
        self.setHorizontalHeaderItem(2, self.header_column(TextConstants.tw_lv_col_initmoisture))
        self.setHorizontalHeaderItem(3, self.header_column(TextConstants.tw_lv_col_erodibility))
        self.setHorizontalHeaderItem(4, self.header_column(TextConstants.tw_lv_col_roughn))
        self.setHorizontalHeaderItem(5, self.header_column(TextConstants.tw_lv_col_cover))
        self.setHorizontalHeaderItem(6, self.header_column(TextConstants.tw_lv_col_skinfactor))

    def header_column(self, text: str) -> QTableWidgetItem:

        item = QTableWidgetItem(text)
        font: QFont = self.font()
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignCenter)

        return item

    def clear_focus(self):
        self.sender().clearFocus()

    def add_cell_item_number(self) -> QLineEdit:
        cell_item = QLineEdit()
        cell_item.setPlaceholderText('0')
        validator = QRegExpValidator(QRegExp(r'^-?[0-9]+[\.,]?[0-9]{0,14}$'))
        cell_item.setValidator(validator)
        cell_item.returnPressed.connect(self.clear_focus)
        return cell_item

    def add_row(self, value: str):

        row_to_put = self.rowCount()

        self.setRowCount(self.rowCount()+1)

        self.setItem(row_to_put, 0, TableItemNotEditable(value))

        for i in range(1, 7):
            self.setCellWidget(row_to_put, i, self.add_cell_item_number())

    def add_data(self, dict_data: Dict[str, Any]):

        if self.rowCount() == 0:

            self.add_all_data(dict_data)

        else:

            input_values = list(dict_data.keys())

            table_values = self.get_table_rownames_values()

            for value in input_values:

                if value not in table_values:
                    self.add_row(value)

            rows_to_remove = []
            for i in range(self.rowCount()):
                if self.item(i, 0).text() not in input_values:
                    rows_to_remove.append(i)

            already_removed = 0
            while 0 < len(rows_to_remove):
                row = rows_to_remove[0]
                self.removeRow(row-already_removed)
                already_removed += 1
                rows_to_remove.remove(row)

    def get_table_rownames_values(self) -> List[str]:

        existing_values = []

        for i in range(self.rowCount()):
            existing_values.append(self.item(i, 0).text())

        return existing_values

    def add_all_data(self, dict_data: Dict[str, Any]):

        for value in list(dict_data.keys()):
            self.add_row(value)

        self.repaint()

    def get_data(self) -> Dict[str, LanduseValues]:

        data = {}

        columns = []

        for i in range(1, self.columnCount()):
            columns.append(self.horizontalHeaderItem(i).text())

        for i in range(self.rowCount()):

            row = {}

            for j in range(1, self.columnCount()):

                value = self.get_value(i, j)

                if value is None:
                    self.any_cell_empty = True

                row.update({columns[j-1]: value})

            data.update({self.get_row_name(i): LanduseValues(self.get_row_name(i),
                                                             row[TextConstants.tw_lv_col_bulkdensity],
                                                             row[TextConstants.tw_lv_col_initmoisture],
                                                             row[TextConstants.tw_lv_col_erodibility],
                                                             row[TextConstants.tw_lv_col_roughn],
                                                             row[TextConstants.tw_lv_col_cover],
                                                             row[TextConstants.tw_lv_col_skinfactor])})

        return data

    def get_row_name(self, row: int) -> str:

        value = self.item(row, 0).text()

        return value

    def get_value(self, row: int, column: int) -> Optional[float]:

        value = self.cellWidget(row, column).text()

        if value == "":
            value = None

        if value:
            value = float(value.replace(",", "."))

        return value
