from typing import Dict

from pathlib import Path


from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QMenu
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from qgis.core import (QgsVectorLayer,
                       QgsFields,
                       QgsFeature,
                       QgsVectorDataProvider)

from ..classes.catalog import E3dCatalog
from ..constants import TextConstants


class TableWidgetLanduseAssignedCatalog(QTableWidget):

    def __init__(self, parent=None,
                 name_subcategory: str = None):

        if name_subcategory is None:
            name_subcategory = TextConstants.tw_lc_sub_cats

        QTableWidget.__init__(self, parent)

        self.name_subcategory = name_subcategory

        self.rows_list = []

        self.catalog = E3dCatalog()

        self.data_dict = self.catalog.get_landuse_crop()

        self.setColumnCount(2)

        item = QTableWidgetItem(TextConstants.tw_lc_col_value)
        font: QFont = self.font()
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignCenter)

        self.setHorizontalHeaderItem(0, item)

        item = QTableWidgetItem(TextConstants.tw_lc_col_assigned)
        font: QFont = self.font()
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignCenter)

        self.setHorizontalHeaderItem(1, item)

        self.setColumnWidth(0, self.columnWidth(1) * 2)
        self.setColumnWidth(1, self.columnWidth(1) * 3)

    @staticmethod
    def filterTheDict(dictObj, callback):
        newDict = dict()
        # Iterate over all the items in dictionary
        for (key, value) in dictObj.items():
            # Check if item satisfies the given condition then add to new dict
            if callback((key, value)):
                newDict[key] = value
        return newDict

    def build_menu(self) -> QPushButton:

        main_menu = QMenu()
        main_menu.triggered.connect(lambda action: button.setText(action.text()))

        main_level = self.filterTheDict(self.data_dict,
                                        lambda elem: elem[1].id_landuse_lv1 == elem[1].id)

        for (name, info) in main_level.items():

            main_menu.addAction(name)

            sublevels_1 = self.filterTheDict(self.data_dict,
                                             lambda elem: elem[1].id_landuse_lv1 == info.id and
                                                          elem[1].id != info.id)

            if len(sublevels_1) > 0:

                menu1 = QMenu(F"{name} - {self.name_subcategory}", main_menu)

                for (sublevel1, info1) in sublevels_1.items():

                    menu1.addAction(sublevel1)

                    menu2 = QMenu(F"{sublevel1} - {self.name_subcategory}", menu1)

                    sublevels_2 = self.filterTheDict(self.data_dict,
                                                     lambda elem: elem[1].id_landuse_lv2 == info1.id and
                                                     elem[1].id != info1.id)

                    if len(sublevels_2) > 0:

                        for sublevel2 in sublevels_2.keys():
                            menu2.addAction(sublevel2)

                        menu1.addMenu(menu2)
                        menu1.addSeparator()

                main_menu.addMenu(menu1)
                main_menu.addSeparator()

        button = QPushButton()
        button.setMenu(main_menu)
        button.setStyleSheet("text-align:left;padding-left: 10px;")
        button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(self.handle_right_click)

        return button

    def handle_right_click(self):
        self.sender().setText(None)

    def add_data(self, data: QgsVectorLayer, field: str):

        fields: QgsFields = data.fields()
        field_index = fields.lookupField(field)

        unique_values = list(data.uniqueValues(field_index))

        if self.rows_list != unique_values:

            self.rows_list = unique_values

            self.setRowCount(len(unique_values))

            for i in range(self.rowCount()):

                self.setItem(i, 0, QTableWidgetItem(unique_values[i]))

                self.setCellWidget(i, 1, self.build_menu())

            self.repaint()

    def is_filled(self):

        rows_filled = [None] * self.rowCount()

        for i in range(self.rowCount()):
            text = self.cellWidget(i, 1).text()
            rows_filled[i] = text is not None and text is not ""

        return all(rows_filled)

    def get_data(self) -> Dict:

        data = {}

        for i in range(self.rowCount()):

            landuse_category = self.item(i, 0).text()
            values = self.cellWidget(i, 1).text()

            if values in self.data_dict.keys():
                data.update({landuse_category: self.data_dict[values]})
            else:
                data.update({landuse_category: None})

        return data

    def get_data_as_layer(self) -> QgsVectorLayer:

        layer = QgsVectorLayer("NoGeometry?field=orig:string&field=new:string&field=landuse_lv1:int&field=landuse_lv2:int&field=crop_id:int",
                               "source",
                               "memory")

        layer_dp: QgsVectorDataProvider = layer.dataProvider()

        for i in range(self.rowCount()):

            text_orig = self.takeItem(i, 0).text()
            text_new = self.cellWidget(i, 1).text()

            if text_new in self.data_dict.keys():
                a = self.data_dict[text_new]
            else:
                a = None

            f = QgsFeature()

            if a:
                f.setAttributes([text_orig, text_new, a["landuse_lv1"], a["landuse_lv2"], a["crop_id"]])
            else:
                f.setAttributes([text_orig, text_new])

            layer_dp.addFeature(f)

        return layer
