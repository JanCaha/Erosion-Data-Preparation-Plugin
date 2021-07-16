# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict
import datetime

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from PyQt5 import QtWidgets, QtCore

from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
from qgis.core import (QgsMapLayerProxyModel,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayer,
                       Qgis,
                       QgsRasterFileWriter,
                       QgsFieldProxyModel,
                       QgsProject,
                       QgsFileUtils,
                       QgsProcessingUtils)

from .algorithms.algs import (calculate_garbrecht_roughness,
                              landuse_with_crops,
                              validate_KA5,
                              classify_KA5,
                              add_fields_to_landuse,
                              add_field_with_constant_value,
                              add_fid_field,
                              save_raster_as_asc)

from .algorithms.algorithms_layers import (join_tables,
                                           intersect_dissolve,
                                           create_table_to_join,
                                           copy_layer_fix_geoms,
                                           create_table_KA5_to_join,
                                           rasterize_layer_by_example)

from .algorithms.extract_elements_from_dicts import (extract_elements_without_values,
                                                     extract_elements_with_values)
from .algorithms.utils import (log,
                               evaluate_result_layer,
                               eval_string_with_variables)

from .gui_classes.table_widget_landuse_assigned_catalog import TableWidgetLanduseAssignedCatalog
from .gui_classes.table_widget_values import TableWidgetLanduseAssignedValues
from .gui_classes.table_widget_with_slider import (TableWidgetBulkDensity,
                                                   TableWidgetCorg,
                                                   TableWidgetCanopyCover,
                                                   TableWidgetRoughness,
                                                   TableWidgetErodibility,
                                                   TableWidgetSkinFactor)

from .classes.definition_landuse_values import LanduseValues
from .classes.definition_landuse_crop import LanduseCrop
from .constants import TextConstants


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
path_ui = Path(__file__).parent / "ui" / "gui_tests_dialog_base.ui"
FORM_CLASS, _ = uic.loadUiType(str(path_ui))


class MainPluginDialog(QtWidgets.QDialog, FORM_CLASS):

    # TODO fix element to remove
    qlabel_i: QtWidgets.QLabel

    qlabel_main: QtWidgets.QLabel
    qlabel_step_description: QtWidgets.QLabel

    # process parameters
    layer_soil: QgsVectorLayer = None
    layer_landuse: QgsVectorLayer = None
    layer_intersected_dissolved: QgsVectorLayer = None
    layer_raster_dtm: QgsRasterLayer = None
    layer_raster_rasterized: QgsRasterLayer = None
    date_month: int = None


    # widget0
    layer_soil_cb: QgsMapLayerComboBox
    layer_landuse_cb: QgsMapLayerComboBox
    raster_dtm_cb: QgsMapLayerComboBox
    calendar: QtWidgets.QCalendarWidget

    # widget1
    field_ka5_cb: QgsFieldComboBox

    # widget2
    layer_soil_cb_2: QgsMapLayerComboBox
    le_field_gb: QtWidgets.QLineEdit
    le_field_d90: QtWidgets.QLineEdit
    cb_addD90: QtWidgets.QCheckBox

    # widget 3
    fcb_ftc: QgsFieldComboBox
    fcb_mtc: QgsFieldComboBox
    fcb_gtc: QgsFieldComboBox
    fcb_fuc: QgsFieldComboBox
    fcb_muc: QgsFieldComboBox
    fcb_guc: QgsFieldComboBox
    fcb_fsc: QgsFieldComboBox
    fcb_msc: QgsFieldComboBox
    fcb_gsc: QgsFieldComboBox

    # widget 4
    fcb_landuse: QgsFieldComboBox
    fcb_crop: QgsFieldComboBox

    # widget 5
    tableView_a: QtWidgets.QTableWidget

    # widget 6
    label_data_status: QtWidgets.QLabel

    # widget last

    label_landuse_raster: QtWidgets.QLabel
    lineEdit_landuse_raster: QtWidgets.QLineEdit
    toolButton_landuse_raster: QtWidgets.QFileDialog

    label_parameter_table: QtWidgets.QLabel
    lineEdit_parameter_table: QtWidgets.QLineEdit
    toolButton_parameter_table: QtWidgets.QFileDialog

    label_lookup_table: QtWidgets.QLabel
    lineEdit_lookup_table: QtWidgets.QLineEdit
    toolButton_lookup_table: QtWidgets.QFileDialog

    # main window
    stackedWidget: QtWidgets.QStackedWidget
    progressBar: QtWidgets.QProgressBar
    button_box: QtWidgets.QDialogButtonBox
    checkbox_export_empty_data: QtWidgets.QCheckBox

    label_created: QtWidgets.QLabel
    label_project: QtWidgets.QLabel

    dict_landuse_values: Dict[str, LanduseValues]
    dict_landuse_crop: Dict[str, LanduseCrop]

    ok_result_layer: bool

    table_bulk_density: TableWidgetBulkDensity
    table_corg: TableWidgetCorg
    table_canopy_cover: TableWidgetCanopyCover
    table_roughness: TableWidgetRoughness
    table_erodibility: TableWidgetErodibility
    table_skinfactor: TableWidgetSkinFactor

    def __init__(self, iface, parent=None):

        super(MainPluginDialog, self).__init__(parent)

        self.iface = iface

        self.ok_result_layer = False

        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)

        self.qlabel_i.setVisible(False)

        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        self.next_pb.clicked.connect(self.__next__)
        self.previous_pb.clicked.connect(self.prev)

        self.stackedWidget.currentChanged.connect(self.update_prev_next_buttons)
        self.stackedWidget.currentChanged.connect(self.set_main_label)

        self.set_main_label()
        self.update_prev_next_buttons()

        self.label_created.setText(TextConstants.label_created)
        self.label_project.setText(TextConstants.label_project)

        # widget 0
        self.layer_soil_cb.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.layer_soil_cb.layerChanged.connect(self.update_layer_soil)
        self.layer_soil_cb.indexChanged(0)

        self.layer_landuse_cb.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.layer_landuse_cb.layerChanged.connect(self.update_layer_landuse)
        self.layer_landuse_cb.indexChanged(0)

        self.raster_dtm_cb.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.raster_dtm_cb.layerChanged.connect(self.update_layer_raster_dtm)
        self.raster_dtm_cb.indexChanged(0)

        self.calendar.selectionChanged.connect(self.update_month)
        self.calendar.setLocale(TextConstants.locale)
        self.date_month = self.calendar.selectedDate().month()

        # widget 1
        self.label_soil_layer.setText(TextConstants.label_soil_layer)
        self.label_landuse_layer.setText(TextConstants.label_landuse_layer)
        self.label_dtm.setText(TextConstants.label_dtm)
        self.label_date.setText(TextConstants.label_date)

        # widget 2
        self.field_ka5_cb.setFilters(QgsFieldProxyModel.String)

        # widget 3
        self.label_FT.setText(TextConstants.label_FT)
        self.label_MT.setText(TextConstants.label_MT)
        self.label_GT.setText(TextConstants.label_GT)
        self.label_FU.setText(TextConstants.label_FU)
        self.label_MU.setText(TextConstants.label_MU)
        self.label_GU.setText(TextConstants.label_GU)
        self.label_FS.setText(TextConstants.label_FS)
        self.label_MS.setText(TextConstants.label_MS)
        self.label_GS.setText(TextConstants.label_GS)

        self.fcb_ftc.setFilters(QgsFieldProxyModel.Numeric)
        self.fcb_mtc.setFilters(QgsFieldProxyModel.Numeric)
        self.fcb_gtc.setFilters(QgsFieldProxyModel.Numeric)
        self.fcb_fuc.setFilters(QgsFieldProxyModel.Numeric)
        self.fcb_muc.setFilters(QgsFieldProxyModel.Numeric)
        self.fcb_guc.setFilters(QgsFieldProxyModel.Numeric)
        self.fcb_fsc.setFilters(QgsFieldProxyModel.Numeric)
        self.fcb_muc.setFilters(QgsFieldProxyModel.Numeric)
        self.fcb_guc.setFilters(QgsFieldProxyModel.Numeric)

        # widget 4
        self.label_crop_field.setText(TextConstants.label_crop_field)
        self.label_landuse_field.setText(TextConstants.label_landuse_field)

        # widget last
        self.label_data_status_confirm.setText(TextConstants.label_data_status_confirm)

        self.label_landuse_raster.setText(TextConstants.label_landuse_raster)
        self.label_lookup_table.setText(TextConstants.label_lookup_table)
        self.label_parameter_table.setText(TextConstants.label_parameter_table)

        self.toolButton_landuse_raster.clicked.connect(self.select_file_landuse_raster)
        self.toolButton_lookup_table.clicked.connect(self.select_file_lookup_table)
        self.toolButton_parameter_table.clicked.connect(self.select_file_parameter_table)

        self.lineEdit_landuse_raster.setText(QgsProcessingUtils.generateTempFilename("landuse_raster.asc"))
        self.lineEdit_parameter_table.setText(QgsProcessingUtils.generateTempFilename("parameter_table.csv"))
        self.lineEdit_lookup_table.setText(QgsProcessingUtils.generateTempFilename("lookup_table.csv"))

        self.fcb_landuse.setFilters(QgsFieldProxyModel.String)
        self.fcb_crop.setFilters(QgsFieldProxyModel.String)

        self.table_landuse_assign_catalog = TableWidgetLanduseAssignedCatalog()
        widget: QtWidgets.QWidget = self.stackedWidget.widget(4)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(4, self.table_landuse_assign_catalog)

        self.table_corg = TableWidgetCorg(TextConstants.header_table_corg)
        widget = self.stackedWidget.widget(5)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(5, self.table_corg)

        self.table_bulk_density = TableWidgetBulkDensity(TextConstants.header_table_bulkdensity)
        widget = self.stackedWidget.widget(6)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(6, self.table_bulk_density)

        self.table_canopy_cover = TableWidgetCanopyCover(TextConstants.header_table_canopycover)
        widget = self.stackedWidget.widget(7)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(7, self.table_canopy_cover)

        self.table_roughness = TableWidgetRoughness(TextConstants.header_table_roughness)
        widget = self.stackedWidget.widget(8)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(8, self.table_roughness)

        self.table_erodibility = TableWidgetErodibility(TextConstants.header_table_erodibility)
        widget = self.stackedWidget.widget(9)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(9, self.table_erodibility)

        self.table_skinfactor = TableWidgetSkinFactor(TextConstants.header_table_skinfactor)
        widget = self.stackedWidget.widget(10)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(10, self.table_skinfactor)

        self.checkbox_export_empty_data.stateChanged.connect(self.allow_ok_button)

    def select_file_landuse_raster(self):
        filter = "asc (*.asc)"
        file_name, type = QtWidgets.QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_landuse_raster.setText(file_name)

    def select_file_lookup_table(self):
        file_name, type = QtWidgets.QFileDialog.getSaveFileName(self, 'Select file')
        self.lineEdit_lookup_table.setText(file_name)

    def select_file_parameter_table(self):
        file_name, type = QtWidgets.QFileDialog.getSaveFileName(self, 'Select file')
        self.lineEdit_parameter_table.setText(file_name)

    def allow_ok_button(self):
        if self.sender().isChecked() or self.ok_result_layer:
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

    def validate_widget_0(self):

        msg = ""

        status = True if self.layer_soil_cb.currentLayer() else False

        if not status:
            msg = TextConstants.msg_select_layer

        return status, msg

    def validate_widget_1(self):

        msg = ""
        ok = True

        if self.field_ka5_cb.currentText():

            ok, missing_values = validate_KA5(self.layer_soil, self.field_ka5_cb.currentText())

            msg = eval_string_with_variables(TextConstants.msg_validate_ka5_classes)

        return ok, msg

    def validate_widget_2(self):

        msg = ""

        status = len(self.fcb_ftc.currentText()) > 0 and \
                 len(self.fcb_mtc.currentText()) > 0 and \
                 len(self.fcb_gtc.currentText()) > 0 and \
                 len(self.fcb_fuc.currentText()) > 0 and \
                 len(self.fcb_muc.currentText()) > 0 and \
                 len(self.fcb_guc.currentText()) > 0 and \
                 len(self.fcb_fsc.currentText()) > 0 and \
                 len(self.fcb_msc.currentText()) > 0 and \
                 len(self.fcb_gsc.currentText()) > 0

        if not status:
            msg = TextConstants.msg_select_all_fields

        return status, msg


    def validate_widget_3(self):
        msg = ""

        status = len(self.fcb_landuse.currentText()) > 0

        if not status:
            msg = TextConstants.mgs_select_landuse_field

        return status, msg

    def update_month(self):
        self.date_month = self.calendar.selectedDate().month()

    def update_layer_raster_dtm(self):

        if self.raster_dtm_cb.currentLayer():
            self.layer_raster_dtm = QgsRasterLayer(self.raster_dtm_cb.currentLayer().source(), "raster_dtm")

    def update_layer_landuse(self):

        if self.layer_landuse_cb.currentLayer():
            self.layer_landuse = QgsVectorLayer(self.layer_landuse_cb.currentLayer().source())

            fields = self.layer_landuse.fields()

            self.fcb_landuse.setFields(fields)
            self.fcb_landuse.setField("LandUse")
            self.fcb_crop.setFields(fields)
            self.fcb_crop.setField("plodina")

    def update_layer_soil(self):

        if self.layer_soil:

            fields = self.layer_soil.fields()

            if not self.field_ka5_cb.currentText():
                self.field_ka5_cb.setFields(fields)
                self.field_ka5_cb.setField("ka5")

            self.fcb_ftc.setFields(fields)
            if "ka5_ft" in fields.names():
                self.fcb_ftc.setField("ka5_ft")
            else:
                self.fcb_ftc.setField("FT")

            self.fcb_mtc.setFields(fields)
            if "ka5_mt" in fields.names():
                self.fcb_mtc.setField("ka5_mt")
            else:
                self.fcb_mtc.setField("MT")

            self.fcb_gtc.setFields(fields)
            if "ka5_gt" in fields.names():
                self.fcb_gtc.setField("ka5_gt")
            else:
                self.fcb_gtc.setField("GT")

            self.fcb_fuc.setFields(fields)
            if "ka5_fu" in fields.names():
                self.fcb_fuc.setField("ka5_fu")
            else:
                self.fcb_fuc.setField("FU")

            self.fcb_muc.setFields(fields)
            if "ka5_mu" in fields.names():
                self.fcb_muc.setField("ka5_mu")
            else:
                self.fcb_muc.setField("MU")

            self.fcb_guc.setFields(fields)
            if "ka5_gu" in fields.names():
                self.fcb_guc.setField("ka5_gu")
            else:
                self.fcb_guc.setField("GU")

            self.fcb_fsc.setFields(fields)
            if "ka5_fs" in fields.names():
                self.fcb_fsc.setField("ka5_fs")
            else:
                self.fcb_fsc.setField("FS")

            self.fcb_msc.setFields(fields)
            if "ka5_ms" in fields.names():
                self.fcb_msc.setField("ka5_ms")
            else:
                self.fcb_msc.setField("MS")

            self.fcb_gsc.setFields(fields)
            if "ka5_gs" in fields.names():
                self.fcb_gsc.setField("ka5_gs")
            else:
                self.fcb_gsc.setField("GS")

    def update_prev_next_buttons(self):
        i = self.stackedWidget.currentIndex()
        self.previous_pb.setEnabled(i > 0)
        self.next_pb.setEnabled(i < self.stackedWidget.count() - 1)

    def set_main_label(self):
        i = self.stackedWidget.currentIndex()

        if i < len(TextConstants.main_labels):
            label = TextConstants.main_labels[i]
        else:
            label = ""

        self.qlabel_main.setText(label)

        if i < len(TextConstants.step_description_labels):
            label = TextConstants.step_description_labels[i]
        else:
            label = ""

        self.qlabel_step_description.setText(label)

    def __next__(self):

        i = self.stackedWidget.currentIndex()

        ok = True
        msg = None

        if i < self.stackedWidget.count():

            self.qlabel_i.setText(F"{i+1}")

            if i == 0:

                ok, msg = self.validate_widget_0()

                if ok:
                    self.layer_soil = copy_layer_fix_geoms(self.layer_soil_cb.currentLayer(),
                                                           TextConstants.layer_soil)

                    self.layer_landuse = copy_layer_fix_geoms(self.layer_landuse_cb.currentLayer(),
                                                              TextConstants.layer_landuse)

                    self.update_layer_soil()

            if i == 1:

                ok, msg = self.validate_widget_1()

                if self.field_ka5_cb.currentText():

                    layer_ka5 = create_table_KA5_to_join()

                    self.layer_soil = join_tables(self.layer_soil,
                                                  self.field_ka5_cb.currentText(),
                                                  layer_ka5,
                                                  TextConstants.field_name_ka5_code,
                                                  progress_bar=self.progressBar)

                    self.update_layer_soil()

            if i == 2:

                ok, msg = self.validate_widget_2()

                if ok:

                    ok, msg = calculate_garbrecht_roughness(self.layer_soil,
                                                            True,
                                                            TextConstants.field_name_d90,
                                                            TextConstants.field_name_GB,
                                                            self.fcb_ftc.currentText(),
                                                            self.fcb_mtc.currentText(),
                                                            self.fcb_gtc.currentText(),
                                                            self.fcb_fuc.currentText(),
                                                            self.fcb_muc.currentText(),
                                                            self.fcb_guc.currentText(),
                                                            self.fcb_fsc.currentText(),
                                                            self.fcb_msc.currentText(),
                                                            self.fcb_gsc.currentText(),
                                                            self.progressBar)

                if ok:

                    ok, msg = classify_KA5(self.layer_soil,
                                           self.fcb_ftc.currentText(),
                                           self.fcb_mtc.currentText(),
                                           self.fcb_gtc.currentText(),
                                           self.fcb_fuc.currentText(),
                                           self.fcb_muc.currentText(),
                                           self.fcb_guc.currentText(),
                                           self.fcb_fsc.currentText(),
                                           self.fcb_msc.currentText(),
                                           self.fcb_gsc.currentText(),
                                           TextConstants.field_name_ka5_code,
                                           TextConstants.field_name_ka5_name,
                                           TextConstants.field_name_ka5_id,
                                           self.progressBar)

            if i == 3:

                ok, msg = self.validate_widget_3()

                if ok:

                    ok, msg = landuse_with_crops(self.layer_landuse,
                                                 self.fcb_landuse.currentText(),
                                                 self.fcb_crop.currentText(),
                                                 self.progressBar)

                self.table_landuse_assign_catalog.add_data(self.layer_landuse,
                                                           TextConstants.field_name_landuse_crops)

            if i == 4:

                ok = True

                if ok:

                    self.dict_landuse_crop = self.table_landuse_assign_catalog.get_data()

                    add_fields_to_landuse(self.layer_landuse,
                                          self.dict_landuse_crop)
                    # TODO SID???
                    dissolve_list = [TextConstants.field_name_ka5_id,
                                     TextConstants.field_name_ka5_name,
                                     TextConstants.field_name_ka5_code,
                                     TextConstants.field_name_ka5_group_lv2_id,
                                     TextConstants.field_name_landuse_lv1_id,
                                     TextConstants.field_name_landuse_lv2_id,
                                     TextConstants.field_name_crop_id,
                                     TextConstants.field_name_crop_name,
                                     TextConstants.field_name_sid,
                                     TextConstants.field_name_landuse_crops]

                    self.layer_intersected_dissolved = intersect_dissolve(self.layer_soil,
                                                                          self.layer_landuse,
                                                                          TextConstants.field_name_poly_id,
                                                                          TextConstants.field_name_sid,
                                                                          TextConstants.field_name_landuse_crops,
                                                                          dissolve_list,
                                                                          progress_bar=self.progressBar)

                    add_field_with_constant_value(self.layer_intersected_dissolved,
                                                  TextConstants.field_name_month,
                                                  self.date_month)

            if i == 4:

                self.table_corg.add_data(self.layer_intersected_dissolved)

            if i == 5:

                self.layer_intersected_dissolved = self.table_corg.join_data(self.layer_intersected_dissolved)

                self.table_bulk_density.add_data(self.layer_intersected_dissolved)

            if i == 6:

                self.layer_intersected_dissolved = self.table_bulk_density.join_data(self.layer_intersected_dissolved)

                self.table_canopy_cover.add_data(self.layer_intersected_dissolved)

            if i == 7:

                self.layer_intersected_dissolved = self.table_canopy_cover.join_data(self.layer_intersected_dissolved)

                self.table_roughness.add_data(self.layer_intersected_dissolved)

            if i == 8:

                self.layer_intersected_dissolved = self.table_roughness.join_data(self.layer_intersected_dissolved)

                self.table_erodibility.add_data(self.layer_intersected_dissolved)

            if i == 9:

                self.layer_intersected_dissolved = self.table_erodibility.join_data(self.layer_intersected_dissolved)

                self.table_skinfactor.add_data(self.layer_intersected_dissolved)

            if i == 10:

                self.layer_intersected_dissolved = self.table_skinfactor.join_data(self.layer_intersected_dissolved)

                add_fid_field(self.layer_intersected_dissolved)

                self.layer_raster_rasterized = rasterize_layer_by_example(self.layer_intersected_dissolved,
                                                                          TextConstants.field_name_fid,
                                                                          self.layer_raster_dtm,
                                                                          progress_bar=self.progressBar)

            if i == 5:

                self.ok_result_layer, msg = evaluate_result_layer(self.layer_intersected_dissolved)

                self.label_data_status.setText(msg)

                if self.ok_result_layer:
                    self.label_data_status.setStyleSheet("color : black;")
                else:
                    self.label_data_status.setStyleSheet("color : red;")

            if i + 1 == self.stackedWidget.count() - 1:

                if self.ok_result_layer or self.checkbox_export_empty_data.isChecked():
                        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

            if ok:
                self.stackedWidget.setCurrentIndex(i + 1)
                self.progressBar.setValue(0)
            else:
                QtWidgets.QMessageBox.warning(self, TextConstants.msg_title, msg)
                self.progressBar.setValue(0)

    def prev(self):
        i = self.stackedWidget.currentIndex()
        self.stackedWidget.setCurrentIndex(i - 1)
        if i != self.stackedWidget.count() - 1:
            self.next_pb.setText('Next >')

        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
