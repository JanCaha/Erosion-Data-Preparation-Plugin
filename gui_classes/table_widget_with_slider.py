import abc
from typing import Dict, Any, List, Optional, Tuple, NoReturn

from qgis.PyQt.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView, QToolButton
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QFont, QRegExpValidator, QColor

from qgis.core import (QgsVectorLayer,
                       QgsVectorDataProvider,
                       QgsFeature)

from ..constants import TextConstants
from ..classes.definition_landuse_values import LanduseValues
from .widget_slider_values import QWidgetSliderValues
from ..algorithms.utils import log
from ..classes.catalog import E3dCatalog
from ..algorithms.utils import (get_unique_fields_combinations, eval_string_with_variables)
from ..algorithms.algorithms_layers import join_tables
from ..algorithms.algs import delete_fields
from .table_widget_item import TableItemNotEditable
from .dialog_data_info import DialogDataInfo


class TableWidgetWithSlider(QTableWidget):
    __metaclass__ = abc.ABCMeta

    data_stored: List
    data_show: List
    temp_data_stored: List
    temp_data_show: List

    COLOR_HIGHLIGHT = QColor(255, 200, 180)
    COLOR_WHITE = QColor(255, 255, 255)

    def __init__(self,
                 column_names: List[str],
                 parent=None):

        QTableWidget.__init__(self, parent)

        self.setSortingEnabled(True)

        self.any_cell_empty = False

        self.column_names = column_names

        self.prepare_header()

    def prepare_header(self):

        self.setColumnCount(len(self.column_names) + 2)

        self.slider_col = len(self.column_names) - 2
        self.value_col = len(self.column_names) - 1
        self.stat_col = len(self.column_names)
        self.link_col = self.stat_col + 1

        for i in range(len(self.column_names)):
            self.setHorizontalHeaderItem(i, self.header_column(self.column_names[i]))

            if self.column_names[i] == TextConstants.col_ka5_code:
                self.setColumnWidth(i, 150)

            else:

                if i == self.slider_col:

                    self.setColumnWidth(self.slider_col,
                                        QWidgetSliderValues(0, 1, 0.5).width() + 5)

                else:

                    self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.setHorizontalHeaderItem(self.stat_col, self.header_column(TextConstants.col_stats))
        self.horizontalHeader().setSectionResizeMode(self.stat_col, QHeaderView.ResizeToContents)
        self.setHorizontalHeaderItem(self.link_col, self.header_column("Info"))
        self.horizontalHeader().setSectionResizeMode(self.link_col, QHeaderView.ResizeToContents)

    def set_row_color(self, row: int,
                      color: Optional[QColor] = None):

        if not color:
            color = self.COLOR_WHITE

        self.item(row, 0).setBackground(color)
        self.item(row, self.stat_col).setBackground(color)

    def header_column(self, text: str) -> QTableWidgetItem:

        item = QTableWidgetItem(text)
        font: QFont = self.font()
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(QtCore.Qt.AlignCenter)

        return item

    def add_cell_item_number(self) -> QLineEdit:
        cell_item = QLineEdit()
        cell_item.setPlaceholderText('0')
        cell_item.setAlignment(QtCore.Qt.AlignRight)
        validator = QRegExpValidator(QRegExp(r'^-?[0-9]+[\.,]?[0-9]{0,14}$'))
        cell_item.setValidator(validator)
        cell_item.returnPressed.connect(self.clear_focus)
        # TODO this can be removed to stop coloring
        cell_item.textChanged.connect(self.change_row_color)
        return cell_item

    def change_row_color(self):
        sender = self.sender()

        row = 0

        for i in range(self.rowCount()):
            if self.cellWidget(i, self.value_col) == sender:
                row = i

        if 0 < len(sender.text()):
            self.set_row_color(row, self.COLOR_WHITE)
        else:
            self.set_row_color(row, self.COLOR_HIGHLIGHT)

    def add_row(self, value: List[str]):

        if not all([x is None for x in value]):

            row_to_put = self.rowCount()
            self.insertRow(self.rowCount())

            for i in range(len(value)):
                self.setItem(row_to_put, i, TableItemNotEditable(value[i]))

            min, max, mean, count = self.get_slider_values(value)

            if 0 < count:

                if "mean" not in locals():
                    mean = 0

                statistics_str = eval_string_with_variables(TextConstants.message_statistics)
            else:
                statistics_str = TextConstants.message_statistics_no_records

            self.setCellWidget(row_to_put, self.value_col, self.add_cell_item_number())

            self.setItem(row_to_put, self.stat_col, TableItemNotEditable(statistics_str))

            if not (min is None and max is None):

                slider = QWidgetSliderValues(min, max, round(mean, 4))
                slider.value_changed.connect(self.set_value_from_slider)

                self.setCellWidget(row_to_put, self.slider_col, slider)
                self.cellWidget(row_to_put, self.value_col).setText(str(round(mean, 4)))

            else:
                # TODO this can be removed to stop coloring
                self.set_row_color(row_to_put, self.COLOR_HIGHLIGHT)

            if 0 < count:

                button = QToolButton()
                button.setText("...")
                button.setEnabled(False)

                button.clicked.connect(self.action_for_button)
                button.setEnabled(True)

                self.setCellWidget(row_to_put, self.link_col, button)

    def action_for_button(self):

        for i in range(self.rowCount()):

            if self.cellWidget(i, self.link_col) == self.sender():

                original_data = self.get_real_data(self.extract_data_list()[i])

                named_row = self.create_named_row_for_catalog(original_data)

                values, sources, quality = self.get_row_data(named_row)

                dialog = DialogDataInfo(self.extract_data_list()[i],
                                        values,
                                        sources,
                                        quality,
                                        parent=self)

                dialog.show()
                dialog.exec_()

    def set_value_from_slider(self):

        for i in range(self.rowCount()):

            if self.cellWidget(i, self.slider_col) == self.sender():

                value = round(self.cellWidget(i, self.slider_col).value(), 6)

                self.cellWidget(i, self.value_col).setText(str(value))

    def table_data_to_strings(self, table_data: List[List[Any]]):

        table_data_str = []

        for row in table_data:

            row_str = [str(x) for x in row]

            table_data_str.append(row_str)

        return table_data_str

    def add_data(self, layer: QgsVectorLayer):

        table_data = get_unique_fields_combinations(layer,
                                                    self.field_list_for_table())

        self.process_passed_data_to_display(table_data)

        table_data = self.data_show

        if self.rowCount() == 0:
            self.add_all_data(table_data)

        else:

            table_existing_data = self.extract_data_list()

            for row in table_data:

                if row not in table_existing_data:
                    self.add_row(row)

            rows_to_remove = []
            for i in range(len(table_existing_data)):
                if table_existing_data[i] not in table_data:
                    rows_to_remove.append(i)

            already_removed = 0
            while 0 < len(rows_to_remove):
                row = rows_to_remove[0]
                self.removeRow(row-already_removed)
                already_removed += 1
                rows_to_remove.remove(row)

    def extract_data_list(self) -> List[List[str]]:

        data_list = []

        for i in range(self.rowCount()):

            row = []

            for j in range(self.slider_col):

                # TODO make sure it does not fall
                if self.item(i, j):
                    row.append(self.item(i, j).text())
                else:
                    row.append(None)

            data_list.append(row)

        return data_list

    def add_all_data(self, table_data: List[List[Any]]):

        for row in table_data:
            self.add_row(row)

        self.repaint()

    def get_slider_values(self, value: List[str]):

        index = self.data_show.index(value)

        values_extract = self.data_stored[index]

        min_val, max_val, mean_val, count_val = self.get_slider_stat_values(values_extract)

        return min_val, max_val, mean_val, count_val

    def get_layer_for_join(self) -> QgsVectorLayer:

        layer = QgsVectorLayer(
            F"NoGeometry?{self.prepare_fields()}",
            "source",
            "memory")

        layer_dp: QgsVectorDataProvider = layer.dataProvider()

        extract_list_rows = self.extract_data_list()

        for i in range(self.rowCount()):
            layer_dp.addFeature(self.prepare_feature_attributes(extract_list_rows, i))

        return layer

    def get_real_data(self, visual_row: List[Any]) -> List[Any]:

        index = self.data_show.index(visual_row)

        return self.data_stored[index]

    def prepare_feature_attributes(self,
                                   extract_list_rows: List[List[Any]],
                                   row_number: int) -> QgsFeature:

        row = self.get_real_data(extract_list_rows[row_number])

        feature = QgsFeature()

        value = self.get_value(row_number, self.value_col)

        if value:
            value = float(value)

        feature.setAttributes(self.values_to_feature_list(row, value))

        return feature

    def join_data(self, layer: QgsVectorLayer) -> QgsVectorLayer:

        delete_fields(layer,
                      fields=self.field_to_add())

        result_layer = join_tables(layer,
                                   self.field_list_for_join(),
                                   self.get_layer_for_join(),
                                   self.field_list_for_join())

        return result_layer

    def get_value(self, row: int, column: int) -> Optional[float]:

        value = self.cellWidget(row, column).text()

        if value == "":
            value = None

        if value:
            value = float(value.replace(",", "."))

        return value

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

    def process_passed_data_to_display(self, table_data: List[List[Any]]):

        self.data_stored = []

        self.data_show = []

        for row in table_data:

            result_string = self.row_to_string(row)

            if result_string:

                self.data_show.append(result_string)

                self.data_stored.append(row)

    @abc.abstractmethod
    def field_to_add(self) -> str:
        return

    @abc.abstractmethod
    def row_to_string(self, row: List[Any]) -> Optional[List[str]]:
        return

    @abc.abstractmethod
    def values_to_feature_list(self, row: List[Any], value: Optional[float]) -> List[Any]:
        return

    @abc.abstractmethod
    def field_list_for_table(self) -> List[str]:
        return

    @abc.abstractmethod
    def field_list_for_join(self) -> List[str]:
        return

    @abc.abstractmethod
    def prepare_fields(self) -> str:
        return

    @abc.abstractmethod
    def get_slider_stat_values(self, values: List[Any]) -> Tuple[float, float, float, float]:
        return

    @abc.abstractmethod
    def create_named_row_for_catalog(self, row: List[Any]) -> Dict[str, Any]:
        return

    @abc.abstractmethod
    def get_row_data(self, row: Dict[str, Any]) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:
        return


class TableWidgetBulkDensity(TableWidgetWithSlider):

    def field_to_add(self) -> str:
        return TextConstants.field_name_bulk_density

    def field_list_for_table(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_soil_id,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_landuse_crops,
                TextConstants.field_name_ka5_group_lv1_id,
                TextConstants.field_name_ka5_group_lv2_id]

    def field_list_for_join(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_soil_id,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_ka5_group_lv1_id,
                TextConstants.field_name_ka5_group_lv2_id]

    def get_slider_stat_values(self, values: List[Any]) -> Tuple[float, float, float, float]:

        return E3dCatalog().get_bulk_density_range(crop=values[0],
                                                   landuse_lv1=values[2],
                                                   landuse_lv2=values[1],
                                                   ka5_class=values[4],
                                                   agrotechnology=values[7],
                                                   ka5_group_lv1=values[9],
                                                   ka5_group_lv2=values[10])

    def row_to_string(self, row: List[Any]) -> Optional[List[str]]:
        if row[3] and row[5]:
            return [row[8], row[3], f"{row[6]} ({row[5]})"]
        else:
            return None

    def prepare_fields(self) -> str:

        fields = [F"field={TextConstants.field_name_crop_id}:string",
                  F"field={TextConstants.field_name_landuse_lv2_id}:string",
                  F"field={TextConstants.field_name_landuse_lv1_id}:string",
                  F"field={TextConstants.field_name_crop_name}:string",
                  F"field={TextConstants.field_name_ka5_id}:string",
                  F"field={TextConstants.field_name_ka5_name}:string",
                  F"field={TextConstants.field_name_soil_id}:string",
                  F"field={TextConstants.field_name_agrotechnology}:string",
                  F"field={TextConstants.field_name_ka5_group_lv1_id}:string",
                  F"field={TextConstants.field_name_ka5_group_lv2_id}:string",
                  F"field={TextConstants.field_name_bulk_density}:integer"]

        fields = "&".join(fields)

        return fields

    def values_to_feature_list(self, row: List[Any], value: Optional[float]) -> List[Any]:

        if value is not None:
            value = int(value)

        return [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[9], row[10], value]

    def create_named_row_for_catalog(self, row: List[Any]) -> Dict[str, Any]:

        return {"ka5_class": row[4],
                "ka5_group_lv1": row[9],
                "ka5_group_lv2": row[10],
                "crop": row[0],
                "landuse_lv1": row[2],
                "landuse_lv2": row[1],
                "agrotechnology": row[7]}

    def get_row_data(self, row: Dict[str, Any]) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:
        return E3dCatalog().get_bulk_density_data(**row)


class TableWidgetCorg(TableWidgetWithSlider):

    def field_to_add(self) -> str:
        return TextConstants.field_name_corg

    def field_list_for_table(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_ka5_group_lv2_id,
                TextConstants.field_name_ka5_code,
                TextConstants.field_name_soil_id,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_landuse_crops,
                TextConstants.field_name_ka5_group_lv1_id]

    def field_list_for_join(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_ka5_group_lv2_id,
                TextConstants.field_name_soil_id,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_ka5_group_lv1_id]

    def row_to_string(self, row: List[Any]) -> Optional[List[str]]:
        if row[3] and row[7]:
            return [row[10], row[3], f"{row[8]} ({row[7]})"]
        else:
            return None

    def get_slider_stat_values(self, values: List[Any]) -> Tuple[float, float, float, float]:
        return E3dCatalog().get_corg_range(ka5_class=values[4],
                                           crop=values[0],
                                           landuse_lv1=values[2],
                                           landuse_lv2=values[1],
                                           ka5_group_lv2=values[6],
                                           agrotechnology=values[9],
                                           ka5_group_lv1=values[11])

    def prepare_fields(self) -> str:

        fields = [F"field={TextConstants.field_name_crop_id}:string",
                  F"field={TextConstants.field_name_landuse_lv2_id}:string",
                  F"field={TextConstants.field_name_landuse_lv1_id}:string",
                  F"field={TextConstants.field_name_crop_name}:string",
                  F"field={TextConstants.field_name_ka5_id}:string",
                  F"field={TextConstants.field_name_ka5_name}:string",
                  F"field={TextConstants.field_name_ka5_group_lv2_id}:string",
                  F"field={TextConstants.field_name_soil_id}:string",
                  F"field={TextConstants.field_name_agrotechnology}:string",
                  F"field={TextConstants.field_name_ka5_group_lv1_id}:string",
                  F"field={TextConstants.field_name_corg}:double"]

        fields = "&".join(fields)

        return fields

    def values_to_feature_list(self, row: List[Any], value: Optional[float]) -> List[Any]:
        return [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[8], row[9], row[11], value]

    def create_named_row_for_catalog(self, row: List[Any]) -> Dict[str, Any]:
        return {"ka5_class": row[4],
                "crop": row[0],
                "landuse_lv1": row[2],
                "landuse_lv2": row[1],
                "ka5_group_lv2": row[6],
                "agrotechnology": row[9],
                "ka5_group_lv1": row[11]}

    def get_row_data(self, row: Dict[str, Any]) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:
        return E3dCatalog().get_corg_data(**row)


class TableWidgetCanopyCover(TableWidgetWithSlider):

    def field_to_add(self) -> str:
        return TextConstants.field_name_canopy_cover

    def field_list_for_table(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_landuse_crops]

    def field_list_for_join(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name]

    def row_to_string(self, row: List[Any]) -> Optional[List[str]]:
        if row[3]:
            return [row[4], row[3]]
        else:
            return None

    def get_slider_stat_values(self, values: List[Any]) -> Tuple[float, float, float, float]:
        return E3dCatalog().get_canopy_cover_range(crop=values[0],
                                                   landuse_lv1=values[2],
                                                   landuse_lv2=values[1])

    def prepare_fields(self) -> str:

        fields = [F"field={TextConstants.field_name_crop_id}:string",
                  F"field={TextConstants.field_name_landuse_lv2_id}:string",
                  F"field={TextConstants.field_name_landuse_lv1_id}:string",
                  F"field={TextConstants.field_name_crop_name}:string",
                  F"field={TextConstants.field_name_canopy_cover}:integer"]

        fields = "&".join(fields)

        return fields

    def values_to_feature_list(self, row: List[Any], value: Optional[float]) -> List[Any]:

        if value is not None:
            value = int(value)

        return [row[0], row[1], row[2], row[3], value]

    def create_named_row_for_catalog(self, row: List[Any]) -> Dict[str, Any]:
        return {"crop": row[0],
                "landuse_lv1": row[2],
                "landuse_lv2": row[1]}

    def get_row_data(self, row: Dict[str, Any]) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:
        return E3dCatalog().get_canopy_cover_data(**row)


class TableWidgetRoughness(TableWidgetWithSlider):

    def field_to_add(self) -> str:
        return TextConstants.field_name_roughness

    def field_list_for_table(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_month,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_surface_conditions,
                TextConstants.field_name_vegetation_conditions,
                TextConstants.field_name_protection_measure,
                TextConstants.field_name_landuse_crops]

    def field_list_for_join(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_month,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_surface_conditions,
                TextConstants.field_name_vegetation_conditions,
                TextConstants.field_name_protection_measure]

    def row_to_string(self, row: List[Any]) -> Optional[List[str]]:
        if row[3]:
            return [row[9], row[3]]
        else:
            return None

    def get_slider_stat_values(self, values: List[Any]) -> Tuple[float, float, float, float]:
        return E3dCatalog().get_roughness_range(crop=values[0],
                                                landuse_lv1=values[2],
                                                landuse_lv2=values[1],
                                                month=values[4],
                                                agrotechnology=values[5],
                                                surface_condition=values[6],
                                                vegetation_condition=values[7],
                                                protection_measure=values[8])

    def prepare_fields(self) -> str:

        fields = [F"field={TextConstants.field_name_crop_id}:string",
                  F"field={TextConstants.field_name_landuse_lv2_id}:string",
                  F"field={TextConstants.field_name_landuse_lv1_id}:string",
                  F"field={TextConstants.field_name_crop_name}:string",
                  F"field={TextConstants.field_name_month}:integer",
                  F"field={TextConstants.field_name_agrotechnology}:string",
                  F"field={TextConstants.field_name_surface_conditions}:string",
                  F"field={TextConstants.field_name_vegetation_conditions}:string",
                  F"field={TextConstants.field_name_protection_measure}:string",
                  F"field={TextConstants.field_name_roughness}:double"]

        fields = "&".join(fields)

        return fields

    def values_to_feature_list(self, row: List[Any], value: Optional[float]) -> List[Any]:
        return [row[0], row[1], row[2], row[3], int(row[4]), row[5], row[6], row[7], row[8], value]

    def create_named_row_for_catalog(self, row: List[Any]) -> Dict[str, Any]:
        return {"crop": row[0],
                "landuse_lv1": row[2],
                "landuse_lv2": row[1],
                "month": row[4],
                "agrotechnology": row[5],
                "surface_condition": row[6],
                "vegetation_condition": row[7],
                "protection_measure": row[8]}

    def get_row_data(self, row: Dict[str, Any]) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:
        return E3dCatalog().get_roughness_data(**row)


class TableWidgetErodibility(TableWidgetWithSlider):

    def field_to_add(self) -> str:
        return TextConstants.field_name_erodibility

    def field_list_for_table(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_soil_id,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_protection_measure,
                TextConstants.field_name_surface_conditions,
                TextConstants.field_name_landuse_crops,
                TextConstants.field_name_ka5_group_lv1_id,
                TextConstants.field_name_ka5_group_lv2_id]

    def field_list_for_join(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_soil_id,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_protection_measure,
                TextConstants.field_name_surface_conditions,
                TextConstants.field_name_ka5_group_lv1_id,
                TextConstants.field_name_ka5_group_lv2_id]

    def row_to_string(self, row: List[Any]) -> Optional[List[str]]:
        if row[3] and row[5]:
            return [row[10], row[3], f"{row[6]} ({row[5]})"]
        else:
            return None

    def get_slider_stat_values(self, values: List[Any]) -> Tuple[float, float, float, float]:
        return E3dCatalog().get_erodibility_range(crop=values[0],
                                                  landuse_lv1=values[2],
                                                  landuse_lv2=values[1],
                                                  ka5_class=values[4],
                                                  agrotechnology=values[7],
                                                  protection_measure=values[8],
                                                  surface_condition=values[9],
                                                  ka5_group_lv1=values[11],
                                                  ka5_group_lv2=values[12])

    def prepare_fields(self) -> str:

        fields = [F"field={TextConstants.field_name_crop_id}:string",
                  F"field={TextConstants.field_name_landuse_lv2_id}:string",
                  F"field={TextConstants.field_name_landuse_lv1_id}:string",
                  F"field={TextConstants.field_name_crop_name}:string",
                  F"field={TextConstants.field_name_ka5_id}:string",
                  F"field={TextConstants.field_name_ka5_name}:string",
                  F"field={TextConstants.field_name_soil_id}:string",
                  F"field={TextConstants.field_name_agrotechnology}:string",
                  F"field={TextConstants.field_name_protection_measure}:string",
                  F"field={TextConstants.field_name_surface_conditions}:string",
                  F"field={TextConstants.field_name_ka5_group_lv1_id}:string",
                  F"field={TextConstants.field_name_ka5_group_lv2_id}:string",
                  F"field={TextConstants.field_name_erodibility}:double"]

        fields = "&".join(fields)

        return fields

    def values_to_feature_list(self, row: List[Any], value: Optional[float]) -> List[Any]:
        return [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[11], row[12], value]

    def create_named_row_for_catalog(self, row: List[Any]) -> Dict[str, Any]:
        return {"crop": row[0],
                "landuse_lv1": row[2],
                "landuse_lv2": row[1],
                "ka5_class": row[4],
                "agrotechnology": row[7],
                "protection_measure": row[8],
                "surface_condition": row[9],
                "ka5_group_lv1": row[11],
                "ka5_group_lv2": row[12]}

    def get_row_data(self, row: Dict[str, Any]) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:
        return E3dCatalog().get_erodibility_data(**row)


class TableWidgetSkinFactor(TableWidgetWithSlider):

    def field_to_add(self) -> str:
        return TextConstants.field_name_skinfactor

    def field_list_for_table(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_soil_id,
                TextConstants.field_name_month,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_protection_measure,
                TextConstants.field_name_surface_conditions,
                TextConstants.field_name_landuse_crops,
                TextConstants.field_name_ka5_group_lv1_id,
                TextConstants.field_name_ka5_group_lv2_id]

    def field_list_for_join(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_soil_id,
                TextConstants.field_name_month,
                TextConstants.field_name_agrotechnology,
                TextConstants.field_name_protection_measure,
                TextConstants.field_name_surface_conditions,
                TextConstants.field_name_ka5_group_lv1_id,
                TextConstants.field_name_ka5_group_lv2_id]

    def row_to_string(self, row: List[Any]) -> Optional[List[str]]:
        if row[3] and row[5]:
            return [row[11], row[3], f"{row[6]} ({row[5]})"]
        else:
            return None

    def get_slider_stat_values(self, values: List[Any]) -> Tuple[float, float, float, float]:
        return E3dCatalog().get_skinfactor_range(crop=values[0],
                                                 landuse_lv1=values[2],
                                                 landuse_lv2=values[1],
                                                 ka5_class=values[4],
                                                 month=values[7],
                                                 agrotechnology=values[8],
                                                 protection_measure=values[9],
                                                 surface_condition=values[10],
                                                 ka5_group_lv1=values[12],
                                                 ka5_group_lv2=values[13])

    def prepare_fields(self) -> str:

        fields = [F"field={TextConstants.field_name_crop_id}:string",
                  F"field={TextConstants.field_name_landuse_lv2_id}:string",
                  F"field={TextConstants.field_name_landuse_lv1_id}:string",
                  F"field={TextConstants.field_name_crop_name}:string",
                  F"field={TextConstants.field_name_ka5_id}:string",
                  F"field={TextConstants.field_name_ka5_name}:string",
                  F"field={TextConstants.field_name_soil_id}:string",
                  F"field={TextConstants.field_name_month}:integer",
                  F"field={TextConstants.field_name_agrotechnology}:string",
                  F"field={TextConstants.field_name_protection_measure}:string",
                  F"field={TextConstants.field_name_surface_conditions}:string",
                  F"field={TextConstants.field_name_ka5_group_lv1_id}:string",
                  F"field={TextConstants.field_name_ka5_group_lv2_id}:string",
                  F"field={TextConstants.field_name_skinfactor}:double"]

        fields = "&".join(fields)

        return fields

    def values_to_feature_list(self, row: List[Any], value: Optional[float]) -> List[Any]:
        return [row[0], row[1], row[2], row[3], row[4], row[5], row[6], int(row[7]), row[8], row[9], row[10], row[12], row[13], value]

    def create_named_row_for_catalog(self, row: List[Any]) -> Dict[str, Any]:
        return {"crop": row[0],
                "landuse_lv1": row[2],
                "landuse_lv2": row[1],
                "ka5_class": row[4],
                "month": row[7],
                "agrotechnology": row[8],
                "protection_measure": row[9],
                "surface_condition": row[10],
                "ka5_group_lv1": row[12],
                "ka5_group_lv2": row[13]}

    def get_row_data(self, row: Dict[str, Any]) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:
        return E3dCatalog().get_skinfactor_data(**row)


class TableWidgetInitMoisture(TableWidgetWithSlider):

    def field_to_add(self) -> str:
        return TextConstants.field_name_init_moisture

    def field_list_for_table(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name,
                TextConstants.field_name_landuse_crops]

    def field_list_for_join(self) -> List[str]:
        return [TextConstants.field_name_crop_id,
                TextConstants.field_name_landuse_lv2_id,
                TextConstants.field_name_landuse_lv1_id,
                TextConstants.field_name_crop_name,
                TextConstants.field_name_ka5_id,
                TextConstants.field_name_ka5_name]

    def row_to_string(self, row: List[Any]) -> Optional[List[str]]:
        if row[3] and row[5]:
            return [row[6], row[3], row[5]]
        else:
            return None

    def get_slider_stat_values(self, values: List[Any]) -> Tuple[float, float, float, float]:
        return E3dCatalog().get_initmoisture_range(crop=values[0],
                                                   landuse_lv1=values[2],
                                                   landuse_lv2=values[1],
                                                   ka5_class=values[4])

    def prepare_fields(self) -> str:

        fields = [F"field={TextConstants.field_name_crop_id}:string",
                  F"field={TextConstants.field_name_landuse_lv2_id}:string",
                  F"field={TextConstants.field_name_landuse_lv1_id}:string",
                  F"field={TextConstants.field_name_crop_name}:string",
                  F"field={TextConstants.field_name_ka5_id}:string",
                  F"field={TextConstants.field_name_ka5_name}:string",
                  F"field={TextConstants.field_name_init_moisture}:double"]

        fields = "&".join(fields)

        return fields

    def values_to_feature_list(self, row: List[Any], value: Optional[float]) -> List[Any]:
        return [row[0], row[1], row[2], row[3], row[4], row[5], value]

    def create_named_row_for_catalog(self, row: List[Any]) -> Dict[str, Any]:
        return {"crop": row[0],
                "landuse_lv1": row[2],
                "landuse_lv2": row[1],
                "ka5_class": row[4]}

    def get_row_data(self, row: Dict[str, Any]) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:
        pass