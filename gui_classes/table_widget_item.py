from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5 import QtCore


class TableItemNotEditable(QTableWidgetItem):

    def __init__(self, text: str):

        super().__init__(text)

        self.setFlags(QtCore.Qt.ItemIsEnabled)
