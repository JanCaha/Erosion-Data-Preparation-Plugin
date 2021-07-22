from typing import Dict

from pathlib import Path


from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QMenu
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from qgis.core import (QgsVectorLayer,
                       QgsFields,
                       QgsFeature,
                       QgsVectorDataProvider,
                       QgsProject)

from ..classes.catalog import E3dCatalog
from ..constants import TextConstants
from ..algorithms.utils import log


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

        self.agrotechnology_dict = self.catalog.get_agrotechnology()
        self.vegetation_dict = self.catalog.get_vegetation_condition()
        self.protection_dict = self.catalog.get_protection_measure()
        self.surface_dict = self.catalog.get_surface_condition()

        self.setColumnCount(6)

        self.setHorizontalHeaderItem(0, self.add_header(TextConstants.tw_lc_col_value))
        self.setHorizontalHeaderItem(1, self.add_header(TextConstants.tw_lc_col_assigned))
        self.setHorizontalHeaderItem(2, self.add_header(TextConstants.tw_lc_col_agrotechnology))
        self.setHorizontalHeaderItem(3, self.add_header(TextConstants.tw_lc_col_vegetation_condition))
        self.setHorizontalHeaderItem(4, self.add_header(TextConstants.tw_lc_col_protection_measure))
        self.setHorizontalHeaderItem(5, self.add_header(TextConstants.tw_lc_col_surface_conditions))

        width_smaller = 0.6

        self.setColumnWidth(0, self.columnWidth(1) * 2)
        self.setColumnWidth(1, self.columnWidth(1) * 2)
        self.setColumnWidth(2, int(self.columnWidth(1) * width_smaller))
        self.setColumnWidth(3, int(self.columnWidth(1) * width_smaller))
        self.setColumnWidth(4, int(self.columnWidth(1) * width_smaller))
        self.setColumnWidth(5, int(self.columnWidth(1) * width_smaller))

    def add_header(self, column_name: str) -> QTableWidgetItem:

        item = QTableWidgetItem(column_name)
        font: QFont = self.font()
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignCenter)

        return item

    @staticmethod
    def filterTheDict(dictObj, callback):
        newDict = dict()
        # Iterate over all the items in dictionary
        for (key, value) in dictObj.items():
            # Check if item satisfies the given condition then add to new dict
            if callback((key, value)):
                newDict[key] = value
        return newDict

    def build_menu_button(self, menu: QMenu) -> QPushButton:

        button = QPushButton()
        button.setMenu(menu)
        button.setStyleSheet("text-align:left;padding-left: 10px;")
        button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(self.handle_right_click)

        return button

    def build_menu_surface_conditions(self) -> QPushButton:

        main_menu = QMenu()
        main_menu.triggered.connect(lambda action: button.setText(action.text()))

        for name in self.surface_dict.keys():
            main_menu.addAction(name)

        button = self.build_menu_button(main_menu)

        return button

    def build_menu_protection_measure(self) -> QPushButton:

        main_menu = QMenu()
        main_menu.triggered.connect(lambda action: button.setText(action.text()))

        for name in self.protection_dict.keys():
            main_menu.addAction(name)

        button = self.build_menu_button(main_menu)

        return button

    def build_menu_vegetation_condition(self) -> QPushButton:

        main_menu = QMenu()
        main_menu.triggered.connect(lambda action: button.setText(action.text()))

        for name in self.vegetation_dict.keys():
            main_menu.addAction(name)

        button = self.build_menu_button(main_menu)

        return button

    def build_menu_agrotechnology(self) -> QPushButton:

        main_menu = QMenu()
        main_menu.triggered.connect(lambda action: button.setText(action.text()))

        for name in self.agrotechnology_dict.keys():

            main_menu.addAction(name)

        button = self.build_menu_button(main_menu)

        return button

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

                self.setCellWidget(i, 2, self.build_menu_agrotechnology())
                self.setCellWidget(i, 3, self.build_menu_vegetation_condition())
                self.setCellWidget(i, 4, self.build_menu_protection_measure())
                self.setCellWidget(i, 5, self.build_menu_surface_conditions())

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

    def get_data_as_layer(self, join_field_name: str) -> QgsVectorLayer:

        fields_str = f"field={join_field_name}:string&" \
                     f"field={TextConstants.field_name_landuse_lv1_id}:int&" \
                     f"field={TextConstants.field_name_landuse_lv2_id}:int&" \
                     f"field={TextConstants.field_name_crop_id}:int&" \
                     f"field={TextConstants.field_name_crop_name}:string&" \
                     f"field={TextConstants.field_name_agrotechnology}:int&" \
                     f"field={TextConstants.field_name_vegetation_conditions}:int&" \
                     f"field={TextConstants.field_name_protection_measure}:int&" \
                     f"field={TextConstants.field_name_surface_conditions}:int"

        layer = QgsVectorLayer(f"NoGeometry?{fields_str}",
                               "source",
                               "memory")

        fields = layer.fields()

        layer_dp: QgsVectorDataProvider = layer.dataProvider()

        for i in range(self.rowCount()):

            text_orig = self.item(i, 0).text()
            text_new = self.cellWidget(i, 1).text()

            if text_new in self.data_dict.keys():
                landuse = self.data_dict[text_new]
            else:
                landuse = None

            agro = self.cellWidget(i, 2).text()

            if agro in self.agrotechnology_dict.keys():
                agro_id = self.agrotechnology_dict[agro]
            else:
                agro_id = None

            vegetation = self.cellWidget(i, 3).text()

            if vegetation in self.vegetation_dict.keys():
                vegetation_id = self.vegetation_dict[vegetation]
            else:
                vegetation_id = None

            protection = self.cellWidget(i, 4).text()

            if protection in self.protection_dict.keys():
                protection_id = self.protection_dict[protection]
            else:
                protection_id = None

            surface = self.cellWidget(i, 5).text()

            if surface in self.surface_dict.keys():
                surface_id = self.surface_dict[surface]
            else:
                surface_id = None

            f = QgsFeature(fields)

            f.setAttribute(fields.lookupField(join_field_name), text_orig)

            if landuse:
                f.setAttribute(fields.lookupField(TextConstants.field_name_landuse_lv1_id), landuse.id_landuse_lv1)
                f.setAttribute(fields.lookupField(TextConstants.field_name_landuse_lv2_id), landuse.id_landuse_lv2)
                f.setAttribute(fields.lookupField(TextConstants.field_name_crop_id), landuse.id_crop)
                f.setAttribute(fields.lookupField(TextConstants.field_name_crop_name), landuse.name)

                if landuse.id_landuse_lv1 == 1:
                    if agro_id:
                        f.setAttribute(fields.lookupField(TextConstants.field_name_agrotechnology),
                                       agro_id)

                    if protection_id:
                        f.setAttribute(fields.lookupField(TextConstants.field_name_protection_measure),
                                       protection_id)

            if vegetation_id:
                f.setAttribute(fields.lookupField(TextConstants.field_name_vegetation_conditions),
                               vegetation_id)

            if surface_id:
                f.setAttribute(fields.lookupField(TextConstants.field_name_surface_conditions),
                               surface_id)

            layer_dp.addFeature(f)

        return layer
