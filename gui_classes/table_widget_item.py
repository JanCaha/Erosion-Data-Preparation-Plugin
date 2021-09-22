from qgis.PyQt.QtWidgets import QTableWidget, QTableWidgetItem
from qgis.PyQt import QtCore


class TableItemNotEditable(QTableWidgetItem):

    def __init__(self, text: str):

        super().__init__(text)

        self.setFlags(QtCore.Qt.ItemIsEnabled)
