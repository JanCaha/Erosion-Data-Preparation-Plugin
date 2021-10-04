# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict, List, Tuple, NoReturn
import math

from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import QVariant

from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
from qgis.core import (QgsMapLayerProxyModel,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsFields,
                       QgsFieldProxyModel,
                       QgsProject,
                       QgsFileUtils,
                       QgsProcessingUtils)

from .algorithms.algs import (landuse_with_crops,
                              validate_KA5,
                              classify_KA5,
                              add_field_with_constant_value,
                              add_fid_field,
                              rename_field,
                              max_value_in_field,
                              add_row_without_geom,
                              delete_features_with_values,
                              delete_fields)

from .algorithms.algorithms_layers import (join_tables,
                                           intersect_dissolve,
                                           copy_layer_fix_geoms,
                                           create_table_KA5_to_join,
                                           rasterize_layer_by_example,
                                           retain_only_fields,
                                           replace_raster_values_by_raster)


from .algorithms.utils import (log,
                               add_maplayer_to_project,
                               evaluate_result_layer,
                               eval_string_with_variables)

from .gui_classes.table_widget_landuse_assigned_catalog import TableWidgetLanduseAssignedCatalog
from .gui_classes.table_widget_with_slider import (TableWidgetBulkDensity,
                                                   TableWidgetCorg,
                                                   TableWidgetCanopyCover,
                                                   TableWidgetRoughness,
                                                   TableWidgetErodibility,
                                                   TableWidgetSkinFactor)
from .gui_classes.table_widget_edit_values import TableWidgetEditNumericValues

from .classes.definition_landuse_values import LanduseValues
from .classes.definition_landuse_crop import LanduseCrop
from .constants import TextConstants


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
path_ui = Path(__file__).parent / "ui" / "gui_tests_dialog_base.ui"
FORM_CLASS, _ = uic.loadUiType(str(path_ui))

DEFAULT_EXPORT_VALUES = {TextConstants.field_name_bulk_density: 1,
                         TextConstants.field_name_corg: 1,
                         TextConstants.field_name_roughness: 1,
                         TextConstants.field_name_canopy_cover: 1,
                         TextConstants.field_name_skinfactor: 1,
                         TextConstants.field_name_erodibility: 1}


class MainPluginDialog(QtWidgets.QDialog, FORM_CLASS):

    landuse_select_widget_index = 4
    corg_widget_index = 6
    bulkdensity_widget_index = corg_widget_index + 1
    canopycover_widget_index = corg_widget_index + 2
    roughness_widget_index = corg_widget_index + 3

    qlabel_main: QtWidgets.QLabel
    qlabel_step_description: QtWidgets.QLabel
    qlabel_steps: QtWidgets.QLabel

    # process parameters
    layer_soil: QgsVectorLayer = None
    layer_soil_input: QgsVectorLayer = None
    layer_landuse: QgsVectorLayer = None
    layer_landuse_fields_backup: QgsFields = None

    layer_soil_interstep: QgsVectorLayer = None
    layer_landuse_interstep: QgsVectorLayer = None

    layer_intersected_dissolved: QgsVectorLayer = None
    layer_raster_dtm: QgsRasterLayer = None
    layer_pour_points_rasterized: QgsRasterLayer = None
    layer_raster_rasterized: QgsRasterLayer = None
    date_month: int = None
    layer_export_parameters: QgsVectorLayer = None
    layer_export_lookup: QgsVectorLayer = None

    layer_channel_elements: QgsVectorLayer = None
    layer_drain_elements: QgsVectorLayer = None
    layer_pour_points: QgsVectorLayer = None

    poly_nr_additons: List[Tuple[int, str]] = []

    next_pb: QtWidgets.QPushButton

    # widget0
    layer_soil_cb: QgsMapLayerComboBox
    layer_landuse_cb: QgsMapLayerComboBox
    raster_dtm_cb: QgsMapLayerComboBox
    calendar: QtWidgets.QCalendarWidget

    # widget1
    field_ka5_cb: QgsFieldComboBox
    label_ka5_class: QtWidgets.QLabel
    label_soil_id: QtWidgets.QLabel
    field_soilid_cb: QgsFieldComboBox

    # widget2
    layer_soil_cb_2: QgsMapLayerComboBox
    le_field_gb: QtWidgets.QLineEdit
    le_field_d90: QtWidgets.QLineEdit
    cb_addD90: QtWidgets.QCheckBox

    # widget 3
    fcb_ftc: QtWidgets.QComboBox
    fcb_mtc: QtWidgets.QComboBox
    fcb_gtc: QtWidgets.QComboBox
    fcb_fuc: QtWidgets.QComboBox
    fcb_muc: QtWidgets.QComboBox
    fcb_guc: QtWidgets.QComboBox
    fcb_fsc: QtWidgets.QComboBox
    fcb_msc: QtWidgets.QComboBox
    fcb_gsc: QtWidgets.QComboBox

    # widget 4
    fcb_landuse: QgsFieldComboBox
    fcb_crop: QgsFieldComboBox

    # widget 6
    label_data_status: QtWidgets.QLabel

    # widget initmoisture
    label_initmoisture_layer: QtWidgets.QLabel
    label_initmoisture_field: QtWidgets.QLabel
    fcb_initmoisture: QgsFieldComboBox
    fcb_initmoisture_layer: QtWidgets.QComboBox

    label_bulk_density_layer: QtWidgets.QLabel
    label_bulk_density_field: QtWidgets.QLabel
    fcb_bulk_density_layer: QtWidgets.QComboBox
    fcb_bulk_density: QgsFieldComboBox

    label_corg_layer: QtWidgets.QLabel
    label_corg_field: QtWidgets.QLabel
    fcb_corg_layer: QtWidgets.QComboBox
    fcb_corg: QgsFieldComboBox

    label_roughness_layer: QtWidgets.QLabel
    label_roughness_field: QtWidgets.QLabel
    fcb_roughness_layer: QtWidgets.QComboBox
    fcb_roughness: QgsFieldComboBox

    label_surface_cover_layer: QtWidgets.QLabel
    label_surface_cover_field: QtWidgets.QLabel
    fcb_surface_cover_layer: QtWidgets.QComboBox
    fcb_surface_cover: QgsFieldComboBox

    # widget optional
    layer_channel_elements_cb: QgsMapLayerComboBox
    layer_drain_elements_cb: QgsMapLayerComboBox
    layer_pour_points_cb: QgsMapLayerComboBox

    label_channel_elements: QtWidgets.QLabel
    label_drain_elements: QtWidgets.QLabel
    label_pour_points: QtWidgets.QLabel

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

    label_pour_points_raster: QtWidgets.QLabel
    lineEdit_pour_points_raster: QtWidgets.QLineEdit
    toolButton_pour_points_raster: QtWidgets.QFileDialog

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

    table_edit_values: TableWidgetEditNumericValues

    field_pour_points_cb: QgsFieldComboBox

    def __init__(self, iface, parent=None):

        super(MainPluginDialog, self).__init__(parent)

        self.iface = iface

        self.ok_result_layer = False

        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)

        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        self.set_steps_label()

        self.next_pb.setText(TextConstants.text_next)
        self.previous_pb.setText(TextConstants.text_previous)

        self.label_step_processing.setText(TextConstants.text_current_step_progress)

        self.next_pb.clicked.connect(self.__next__)
        self.previous_pb.clicked.connect(self.prev)

        self.progressBar.setMaximum(1)
        self.progressBar.setValue(1)

        self.stackedWidget.currentChanged.connect(self.update_prev_next_buttons)
        self.stackedWidget.currentChanged.connect(self.set_main_label)
        self.stackedWidget.currentChanged.connect(self.set_steps_label)

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
        self.label_ka5_class.setText(TextConstants.label_ka5_class)
        self.label_soil_id.setText(TextConstants.label_soil_id)
        self.field_soilid_cb.setFilters(QgsFieldProxyModel.String | QgsFieldProxyModel.Int)
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

        # widget 4
        self.label_crop_field.setText(TextConstants.label_crop_field)
        self.label_landuse_field.setText(TextConstants.label_landuse_field)

        self.label_bulk_density_field.setText(TextConstants.label_bulkdensity)
        self.label_bulk_density_layer.setText(TextConstants.label_bulkdensity_layer)
        self.fcb_bulk_density_layer.currentIndexChanged.connect(self.update_bulkdensity_fields)

        self.label_corg_field.setText(TextConstants.label_corg)
        self.label_corg_layer.setText(TextConstants.label_corg_layer)
        self.fcb_corg_layer.currentIndexChanged.connect(self.update_corg_fields)

        self.label_initmoisture_field.setText(TextConstants.label_initmoisture)
        self.label_initmoisture_layer.setText(TextConstants.label_initmoisture_layer)
        self.fcb_initmoisture_layer.currentIndexChanged.connect(self.update_initmoisture_fields)

        self.label_roughness_field.setText(TextConstants.label_roughness)
        self.label_roughness_layer.setText(TextConstants.label_roughness_layer)
        self.fcb_roughness_layer.currentIndexChanged.connect(self.update_roughness_fields)

        self.label_surface_cover_field.setText(TextConstants.label_surfacecover)
        self.label_surface_cover_layer.setText(TextConstants.label_surfacecover_layer)
        self.fcb_surface_cover_layer.currentIndexChanged.connect(self.update_surfacecover_fields)

        # widget optional

        self.label_pour_points.setText(TextConstants.label_pour_points)
        self.label_drain_elements.setText(TextConstants.label_drain_elements)
        self.label_channel_elements.setText(TextConstants.label_channel_elements)

        self.layer_channel_elements_cb.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.layer_channel_elements_cb.layerChanged.connect(self.update_layer_channel_elements)
        self.layer_channel_elements_cb.setCurrentIndex(0)

        self.layer_drain_elements_cb.setFilters(QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer)
        self.layer_drain_elements_cb.layerChanged.connect(self.update_layer_drain_elements)
        self.layer_drain_elements_cb.setCurrentIndex(0)

        self.layer_pour_points_cb.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.layer_pour_points_cb.layerChanged.connect(self.update_layer_pour_points)
        self.layer_pour_points_cb.setCurrentIndex(0)

        self.label_pour_points_identifier.setText(TextConstants.label_pour_points_identifier)
        self.field_pour_points_cb.setFilters(QgsFieldProxyModel.Int)

        # widget lasts
        self.label_data_status_confirm.setText(TextConstants.label_data_status_confirm)

        self.label_landuse_raster.setText(TextConstants.label_landuse_raster)
        self.label_lookup_table.setText(TextConstants.label_lookup_table)
        self.label_parameter_table.setText(TextConstants.label_parameter_table)

        self.toolButton_landuse_raster.clicked.connect(self.select_file_landuse_raster)
        self.toolButton_lookup_table.clicked.connect(self.select_file_lookup_table)
        self.toolButton_parameter_table.clicked.connect(self.select_file_parameter_table)
        self.toolButton_pour_points_raster.clicked.connect(self.select_file_pour_points_raster)

        project_path = QgsProject.instance().absolutePath()

        if project_path != "":
            project_path = Path(project_path)

            self.lineEdit_landuse_raster.setText(str(project_path / "landuse_raster.asc"))
            self.lineEdit_parameter_table.setText(str(project_path / "parameter_table.csv"))
            self.lineEdit_lookup_table.setText(str(project_path / "lookup_table.csv"))
            self.lineEdit_pour_points_raster.setText(str(project_path / "pour.asc"))

        else:
            self.lineEdit_landuse_raster.setText(QgsProcessingUtils.generateTempFilename("landuse_raster.asc"))
            self.lineEdit_parameter_table.setText(QgsProcessingUtils.generateTempFilename("parameter_table.csv"))
            self.lineEdit_lookup_table.setText(QgsProcessingUtils.generateTempFilename("lookup_table.csv"))
            self.lineEdit_pour_points_raster.setText(QgsProcessingUtils.generateTempFilename("pour.asc"))

        self.lineEdit_pour_points_raster.setEnabled(False)
        self.toolButton_pour_points_raster.setEnabled(False)

        self.fcb_landuse.setFilters(QgsFieldProxyModel.String)
        self.fcb_crop.setFilters(QgsFieldProxyModel.String)

        self.table_landuse_assign_catalog = TableWidgetLanduseAssignedCatalog()
        widget: QtWidgets.QWidget = self.stackedWidget.widget(self.landuse_select_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.landuse_select_widget_index, self.table_landuse_assign_catalog)

        self.table_corg = TableWidgetCorg(TextConstants.header_table_corg)
        widget = self.stackedWidget.widget(self.corg_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.corg_widget_index, self.table_corg)

        self.table_bulk_density = TableWidgetBulkDensity(TextConstants.header_table_bulkdensity)
        widget = self.stackedWidget.widget(self.bulkdensity_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.bulkdensity_widget_index, self.table_bulk_density)

        self.table_canopy_cover = TableWidgetCanopyCover(TextConstants.header_table_canopycover)
        widget = self.stackedWidget.widget(self.canopycover_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.canopycover_widget_index, self.table_canopy_cover)

        self.table_roughness = TableWidgetRoughness(TextConstants.header_table_roughness)
        widget = self.stackedWidget.widget(self.roughness_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.roughness_widget_index, self.table_roughness)

        self.table_erodibility = TableWidgetErodibility(TextConstants.header_table_erodibility)
        widget = self.stackedWidget.widget(self.corg_widget_index+4)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.corg_widget_index+4, self.table_erodibility)

        self.table_skinfactor = TableWidgetSkinFactor(TextConstants.header_table_skinfactor)
        widget = self.stackedWidget.widget(self.corg_widget_index+5)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.corg_widget_index+5, self.table_skinfactor)

        self.table_edit_values = TableWidgetEditNumericValues()
        widget = self.stackedWidget.widget(self.corg_widget_index + 7)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.corg_widget_index + 7, self.table_edit_values)

        self.checkbox_export_empty_data.stateChanged.connect(self.allow_ok_button)

    def select_file_pour_points_raster(self):
        filter = "asc (*.asc)"
        file_name, type = QtWidgets.QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_pour_points_raster.setText(file_name)

    def select_file_landuse_raster(self):
        filter = "asc (*.asc)"
        file_name, type = QtWidgets.QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_landuse_raster.setText(file_name)

    def select_file_lookup_table(self):
        filter = "csv (*.csv)"
        file_name, type = QtWidgets.QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_lookup_table.setText(file_name)

    def select_file_parameter_table(self):
        filter = "csv (*.csv)"
        file_name, type = QtWidgets.QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
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

        if not self.field_soilid_cb.currentText():

            ok = False
            msg = TextConstants.msg_select_soil_id

        if ok:

            if self.field_ka5_cb.currentText():

                ok, missing_values = validate_KA5(self.layer_soil, self.field_ka5_cb.currentText())

                msg = eval_string_with_variables(TextConstants.msg_validate_ka5_classes)

        return ok, msg

    def validate_widget_2(self):

        msg = ""

        status = len(self.fcb_mtc.currentText()) > 0 and \
                 len(self.fcb_muc.currentText()) > 0 and \
                 len(self.fcb_msc.currentText()) > 0

        if not status:
            msg = TextConstants.msg_select_all_fields

        if status:

            boxes = [self.fcb_ftc, self.fcb_mtc, self.fcb_gtc,
                     self.fcb_fuc, self.fcb_muc, self.fcb_guc,
                     self.fcb_fsc, self.fcb_msc, self.fcb_gsc]

            status = self.cb_unique_values(boxes) == (9 - self.cb_number_empty(boxes))

            if not status:
                msg = TextConstants.msg_unique_fields

        return status, msg

    def validate_widget_3(self):
        msg = ""

        status = len(self.fcb_landuse.currentText()) > 0

        if not status:
            msg = TextConstants.mgs_select_landuse_field

        return status, msg

    def update_layer_channel_elements(self):

        if 0 < len(self.layer_channel_elements_cb.currentText()):

            self.layer_channel_elements = copy_layer_fix_geoms(self.layer_channel_elements_cb.currentLayer(),
                                                               TextConstants.layer_channel_elements)

        else:
            self.layer_channel_elements = None

    def update_layer_drain_elements(self):

        if 0 < len(self.layer_drain_elements_cb.currentText()):

            self.layer_drain_elements = copy_layer_fix_geoms(self.layer_drain_elements_cb.currentLayer(),
                                                             TextConstants.layer_drain_elements)

        else:
            self.layer_drain_elements = None

    def update_layer_pour_points(self):
        self.layer_pour_points = self.layer_pour_points_cb.currentLayer()

        fields = self.layer_pour_points.fields()

        self.field_pour_points_cb.setFields(fields)
        self.field_pour_points_cb.setCurrentIndex(0)

    def update_month(self):
        self.date_month = self.calendar.selectedDate().month()

    def update_layer_raster_dtm(self):

        if self.raster_dtm_cb.currentLayer():
            self.layer_raster_dtm = self.raster_dtm_cb.currentLayer()

    def update_layer_landuse(self):

        if self.layer_landuse_cb.currentLayer():

            fields = self.layer_landuse_cb.currentLayer().fields()

            self.fcb_landuse.setFields(fields)

            if "LandUse" in fields.names():
                self.fcb_landuse.setField("LandUse")

            self.fcb_crop.setFields(fields)

            if "plodina" in fields.names():
                self.fcb_crop.setField("plodina")

    def update_layer_soil(self):

        if self.layer_soil:

            fields = self.layer_soil.fields()

            field_names = [""]

            fields_to_remove = ["fid", "objectid", "shape_length", "shape_area"]

            for field_to_remove in fields_to_remove:
                index = fields.lookupField(field_to_remove)
                if index != -1:
                    fields.remove(index)

            for field in fields:
                if field.name() not in fields_to_remove:
                    if field.isNumeric():
                        field_names.append(field.name())

            if not self.field_soilid_cb.currentText():
                self.field_soilid_cb.setFields(fields)

            if not self.field_ka5_cb.currentText():
                self.field_ka5_cb.setFields(fields)
                self.field_ka5_cb.setField("ka5")

            self.add_field_names_and_set_selected_back(self.fcb_ftc, field_names)
            self.add_field_names_and_set_selected_back(self.fcb_mtc, field_names)
            self.add_field_names_and_set_selected_back(self.fcb_gtc, field_names)
            self.add_field_names_and_set_selected_back(self.fcb_fuc, field_names)
            self.add_field_names_and_set_selected_back(self.fcb_muc, field_names)
            self.add_field_names_and_set_selected_back(self.fcb_guc, field_names)
            self.add_field_names_and_set_selected_back(self.fcb_fsc, field_names)
            self.add_field_names_and_set_selected_back(self.fcb_msc, field_names)
            self.add_field_names_and_set_selected_back(self.fcb_gsc, field_names)

    @staticmethod
    def add_field_names_and_set_selected_back(combo_box: QtWidgets.QComboBox,
                                              items: List[str]) -> NoReturn:
        index = None

        if combo_box.currentText() != "":
            index = items.index(combo_box.currentText())

        combo_box.clear()
        combo_box.addItems(items)

        if index:
            combo_box.setCurrentIndex(index)

    def update_value_layers(self):

        for i in range(self.fcb_initmoisture_layer.count()):
            self.fcb_initmoisture_layer.removeItem(i)

        fcbs = [self.fcb_initmoisture_layer, self.fcb_corg_layer, self.fcb_bulk_density_layer,
                self.fcb_roughness_layer, self.fcb_surface_cover_layer]

        for fcb in fcbs:

            fcb.clear()
            fcb.addItem("")
            fcb.addItem(f"Soil layer: {self.layer_soil_cb.currentLayer().name()}")
            fcb.addItem(f"Landuse layer: {self.layer_landuse_cb.currentLayer().name()}")

    def update_bulkdensity_fields(self):

        if 0 < len(self.fcb_bulk_density_layer.currentText()):

            if "Soil" in self.fcb_bulk_density_layer.currentText():

                fields: QgsFields = self.layer_soil_cb.currentLayer().fields()

            elif "Landuse" in self.fcb_bulk_density_layer.currentText():

                fields: QgsFields = self.layer_landuse_cb.currentLayer().fields()

            self.fcb_bulk_density.setFields(fields)
            self.fcb_bulk_density.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_bulk_density.setCurrentIndex(0)

        else:
            self.fcb_bulk_density.setFields(QgsFields())

    def update_corg_fields(self):

        if 0 < len(self.fcb_corg_layer.currentText()):

            if "Soil" in self.fcb_corg_layer.currentText():

                fields: QgsFields = self.layer_soil_cb.currentLayer().fields()

            elif "Landuse" in self.fcb_corg_layer.currentText():

                fields: QgsFields = self.layer_landuse_cb.currentLayer().fields()

            self.fcb_corg.setFields(fields)
            self.fcb_corg.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_corg.setCurrentIndex(0)

        else:
            self.fcb_corg.setFields(QgsFields())

    def update_roughness_fields(self):

        if 0 < len(self.fcb_roughness_layer.currentText()):

            if "Soil" in self.fcb_roughness_layer.currentText():

                fields: QgsFields = self.layer_soil_cb.currentLayer().fields()

            elif "Landuse" in self.fcb_roughness_layer.currentText():

                fields: QgsFields = self.layer_landuse_cb.currentLayer().fields()

            self.fcb_roughness.setFields(fields)
            self.fcb_roughness.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_roughness.setCurrentIndex(0)

        else:
            self.fcb_roughness.setFields(QgsFields())

    def update_surfacecover_fields(self):

        if 0 < len(self.fcb_surface_cover_layer.currentText()):

            if "Soil" in self.fcb_surface_cover_layer.currentText():

                fields: QgsFields = self.layer_soil_cb.currentLayer().fields()

            elif "Landuse" in self.fcb_surface_cover_layer.currentText():

                fields: QgsFields = self.layer_landuse_cb.currentLayer().fields()

            self.fcb_surface_cover.setFields(fields)
            self.fcb_surface_cover.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_surface_cover.setCurrentIndex(0)

        else:
            self.fcb_surface_cover.setFields(QgsFields())

    def update_initmoisture_fields(self):

        if 0 < len(self.fcb_initmoisture_layer.currentText()):

            if "Soil" in self.fcb_initmoisture_layer.currentText():

                fields: QgsFields = self.layer_soil_cb.currentLayer().fields()

            elif "Landuse" in self.fcb_initmoisture_layer.currentText():

                fields: QgsFields = self.layer_landuse_cb.currentLayer().fields()

            self.fcb_initmoisture.setFields(fields)
            self.fcb_initmoisture.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_initmoisture.setCurrentIndex(0)

        else:
            self.fcb_initmoisture.setFields(QgsFields())

    def rename_corg(self):

        if 0 < len(self.fcb_corg.currentText()):

            if "Soil" in self.fcb_corg_layer.currentText():

                rename_field(self.layer_soil,
                             self.fcb_corg.currentText(),
                             TextConstants.field_name_corg)

            elif "Landuse" in self.fcb_corg_layer.currentText():

                rename_field(self.layer_landuse,
                             self.fcb_corg.currentText(),
                             TextConstants.field_name_corg)

    def rename_bulkdensity(self):

        if 0 < len(self.fcb_bulk_density.currentText()):

            if "Soil" in self.fcb_bulk_density_layer.currentText():

                rename_field(self.layer_soil,
                             self.fcb_bulk_density.currentText(),
                             TextConstants.field_name_bulk_density)

            elif "Landuse" in self.fcb_bulk_density_layer.currentText():

                rename_field(self.layer_landuse,
                             self.fcb_bulk_density.currentText(),
                             TextConstants.field_name_bulk_density)

    def rename_roughness(self):

        if 0 < len(self.fcb_roughness.currentText()):

            if "Soil" in self.fcb_roughness_layer.currentText():

                rename_field(self.layer_soil,
                             self.fcb_roughness.currentText(),
                             TextConstants.field_name_roughness)

            elif "Landuse" in self.fcb_roughness_layer.currentText():

                rename_field(self.layer_landuse,
                             self.fcb_roughness.currentText(),
                             TextConstants.field_name_roughness)

    def rename_cover(self):

        if 0 < len(self.fcb_surface_cover.currentText()):

            if "Soil" in self.fcb_surface_cover_layer.currentText():

                rename_field(self.layer_soil,
                             self.fcb_surface_cover.currentText(),
                             TextConstants.field_name_canopy_cover)

            elif "Landuse" in self.fcb_surface_cover_layer.currentText():

                rename_field(self.layer_landuse,
                             self.fcb_surface_cover.currentText(),
                             TextConstants.field_name_canopy_cover)

    def rename_initmoisture(self):

        if 0 < len(self.fcb_initmoisture.currentText()):

            if "Soil" in self.fcb_initmoisture_layer.currentText():

                rename_field(self.layer_soil,
                             self.fcb_initmoisture.currentText(),
                             TextConstants.field_name_init_moisture)

            elif "Landuse" in self.fcb_initmoisture_layer.currentText():

                rename_field(self.layer_landuse,
                             self.fcb_initmoisture.currentText(),
                             TextConstants.field_name_init_moisture)

        else:

            add_field_with_constant_value(self.layer_soil,
                                          TextConstants.field_name_init_moisture,
                                          math.nan)

    def update_prev_next_buttons(self):
        i = self.stackedWidget.currentIndex()
        self.previous_pb.setEnabled(i > 0)
        self.next_pb.setEnabled(i < self.stackedWidget.count() - 1)

    def set_steps_label(self):
        self.qlabel_steps.setText(TextConstants.label_steps + str(self.stackedWidget.currentIndex()+1) +
                                  TextConstants.label_from + str(self.stackedWidget.count()) + TextConstants.label_dot)

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

            if i == 0:

                ok, msg = self.validate_widget_0()

                if ok:
                    self.layer_soil_input = copy_layer_fix_geoms(self.layer_soil_cb.currentLayer(),
                                                                 TextConstants.layer_soil)
                    self.layer_soil = self.layer_soil_input

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

                    self.layer_soil_input = self.layer_soil

            if i == 2:

                self.layer_soil = self.layer_soil_input.clone()

                ok, msg = self.validate_widget_2()

                if ok:

                    rename_field(self.layer_soil,
                                 self.field_soilid_cb.currentText(),
                                 TextConstants.field_name_soil_id)

                    self.progressBar.setMaximum(4)
                    self.progressBar.setValue(1)

                    # this three columns exists so rename them
                    fields_to_delete = []

                    if self.fcb_mtc.currentText() != TextConstants.field_name_MT and \
                            TextConstants.field_name_MT in self.layer_soil.fields().names():

                        fields_to_delete.append(TextConstants.field_name_MT)

                    if self.fcb_muc.currentText() != TextConstants.field_name_MU and \
                            TextConstants.field_name_MU in self.layer_soil.fields().names():

                        fields_to_delete.append(TextConstants.field_name_MU)

                    if self.fcb_msc.currentText() != TextConstants.field_name_MS and \
                            TextConstants.field_name_MS in self.layer_soil.fields().names():

                        fields_to_delete.append(TextConstants.field_name_MS)

                    if 0 < len(fields_to_delete):
                        delete_fields(self.layer_soil,
                                      fields_to_delete)

                    rename_field(self.layer_soil,
                                 self.fcb_mtc.currentText(),
                                 TextConstants.field_name_MT)

                    rename_field(self.layer_soil,
                                 self.fcb_muc.currentText(),
                                 TextConstants.field_name_MU)

                    rename_field(self.layer_soil,
                                 self.fcb_msc.currentText(),
                                 TextConstants.field_name_MS)

                    self.progressBar.setValue(2)

                    # these six columns may or may not be set, so either rename or create with 0 value

                    if 0 < len(self.fcb_ftc.currentText()):

                        delete_fields(self.layer_soil,
                                      TextConstants.field_name_FT)

                        rename_field(self.layer_soil,
                                     self.fcb_ftc.currentText(),
                                     TextConstants.field_name_FT)

                    else:

                        add_field_with_constant_value(self.layer_soil,
                                                      TextConstants.field_name_FT,
                                                      0)

                    if 0 < len(self.fcb_gtc.currentText()):

                        delete_fields(self.layer_soil,
                                      TextConstants.field_name_GT)

                        rename_field(self.layer_soil,
                                     self.fcb_gtc.currentText(),
                                     TextConstants.field_name_GT)

                    else:

                        add_field_with_constant_value(self.layer_soil,
                                                      TextConstants.field_name_GT,
                                                      0)

                    if 0 < len(self.fcb_fuc.currentText()):

                        delete_fields(self.layer_soil,
                                      TextConstants.field_name_FU)

                        rename_field(self.layer_soil,
                                     self.fcb_fuc.currentText(),
                                     TextConstants.field_name_FU)

                    else:

                        add_field_with_constant_value(self.layer_soil,
                                                      TextConstants.field_name_FU,
                                                      0)

                    if 0 < len(self.fcb_guc.currentText()):

                        delete_fields(self.layer_soil,
                                      TextConstants.field_name_GU)

                        rename_field(self.layer_soil,
                                     self.fcb_guc.currentText(),
                                     TextConstants.field_name_GU)
                    else:

                        add_field_with_constant_value(self.layer_soil,
                                                      TextConstants.field_name_GU,
                                                      0)

                    if 0 < len(self.fcb_fsc.currentText()):

                        delete_fields(self.layer_soil,
                                      TextConstants.field_name_FS)

                        rename_field(self.layer_soil,
                                     self.fcb_fsc.currentText(),
                                     TextConstants.field_name_FS)
                    else:

                        add_field_with_constant_value(self.layer_soil,
                                                      TextConstants.field_name_FS,
                                                      0)

                    if 0 < len(self.fcb_gsc.currentText()):

                        delete_fields(self.layer_soil,
                                      TextConstants.field_name_GS)

                        rename_field(self.layer_soil,
                                     self.fcb_gsc.currentText(),
                                     TextConstants.field_name_GS)

                    else:

                        add_field_with_constant_value(self.layer_soil,
                                                      TextConstants.field_name_GS,
                                                      0)

                    self.progressBar.setValue(3)

                    ok, msg = classify_KA5(self.layer_soil,
                                           TextConstants.field_name_FT,
                                           TextConstants.field_name_MT,
                                           TextConstants.field_name_GT,
                                           TextConstants.field_name_FU,
                                           TextConstants.field_name_MU,
                                           TextConstants.field_name_GU,
                                           TextConstants.field_name_FS,
                                           TextConstants.field_name_MS,
                                           TextConstants.field_name_GS,
                                           TextConstants.field_name_ka5_code,
                                           TextConstants.field_name_ka5_name,
                                           TextConstants.field_name_ka5_id,
                                           self.progressBar)

                    self.progressBar.setValue(4)

            if i == 3:

                ok, msg = self.validate_widget_3()

                if ok:

                    ok, msg = landuse_with_crops(self.layer_landuse,
                                                 self.fcb_landuse.currentText(),
                                                 self.fcb_crop.currentText(),
                                                 self.progressBar)

                    self.layer_landuse_fields_backup = self.layer_landuse.fields()

                self.table_landuse_assign_catalog.add_data(self.layer_landuse,
                                                           TextConstants.field_name_landuse_crops)

            if i == 4:

                ok = True

                if ok:

                    table = self.table_landuse_assign_catalog.get_data_as_layer(TextConstants.field_name_landuse_crops)

                    self.layer_landuse = retain_only_fields(self.layer_landuse,
                                                            self.layer_landuse_fields_backup.names())

                    self.layer_landuse = join_tables(self.layer_landuse,
                                                     TextConstants.field_name_landuse_crops,
                                                     table,
                                                     TextConstants.field_name_landuse_crops,
                                                     self.progressBar)

                    self.update_value_layers()

                    self.layer_soil_interstep = self.layer_soil
                    self.layer_landuse_interstep = self.layer_landuse

            if i == 5:

                self.layer_landuse = self.layer_landuse_interstep
                self.layer_soil = self.layer_soil_interstep

                self.rename_initmoisture()

                dissolve_list = [TextConstants.field_name_ka5_id,
                                 TextConstants.field_name_ka5_name,
                                 TextConstants.field_name_ka5_code,
                                 TextConstants.field_name_ka5_group_lv2_id,
                                 TextConstants.field_name_landuse_lv1_id,
                                 TextConstants.field_name_landuse_lv2_id,
                                 TextConstants.field_name_crop_id,
                                 TextConstants.field_name_crop_name,
                                 TextConstants.field_name_soil_id,
                                 TextConstants.field_name_landuse_crops,
                                 TextConstants.field_name_poly_id,
                                 TextConstants.field_name_FU,
                                 TextConstants.field_name_MU,
                                 TextConstants.field_name_GU,
                                 TextConstants.field_name_FT,
                                 TextConstants.field_name_MT,
                                 TextConstants.field_name_GT,
                                 TextConstants.field_name_FS,
                                 TextConstants.field_name_MS,
                                 TextConstants.field_name_GS,
                                 TextConstants.field_name_agrotechnology,
                                 TextConstants.field_name_protection_measure,
                                 TextConstants.field_name_vegetation_conditions,
                                 TextConstants.field_name_surface_conditions,
                                 TextConstants.field_name_init_moisture]

                if self.skip_step_table_corg():

                    self.rename_corg()

                    dissolve_list = dissolve_list + [TextConstants.field_name_corg]

                if self.skip_step_table_bulkdensity():

                    self.rename_bulkdensity()

                    dissolve_list = dissolve_list + [TextConstants.field_name_bulk_density]

                if self.skip_step_table_roughness():

                    self.rename_roughness()

                    dissolve_list = dissolve_list + [TextConstants.field_name_roughness]

                if self.skip_step_table_surfacecover():

                    self.rename_cover()

                    dissolve_list = dissolve_list + [TextConstants.field_name_canopy_cover]

                self.layer_intersected_dissolved = intersect_dissolve(self.layer_soil,
                                                                      self.layer_landuse,
                                                                      TextConstants.field_name_poly_id,
                                                                      TextConstants.field_name_soil_id,
                                                                      TextConstants.field_name_landuse_crops,
                                                                      dissolve_list,
                                                                      progress_bar=self.progressBar)

                add_field_with_constant_value(self.layer_intersected_dissolved,
                                              TextConstants.field_name_month,
                                              self.date_month)

                if not self.skip_step_table_corg():
                    self.table_corg.add_data(self.layer_intersected_dissolved)

                else:

                    i += 1

            if i == 6:

                if not self.skip_step_table_corg():
                    self.layer_intersected_dissolved = self.table_corg.join_data(self.layer_intersected_dissolved)

                if not self.skip_step_table_bulkdensity():
                    self.table_bulk_density.add_data(self.layer_intersected_dissolved)

                else:

                    i += 1

            if i == 7:

                if not self.skip_step_table_bulkdensity():
                    self.layer_intersected_dissolved = self.table_bulk_density.join_data(self.layer_intersected_dissolved)

                if not self.skip_step_table_surfacecover():
                    self.table_canopy_cover.add_data(self.layer_intersected_dissolved)

                else:

                    i += 1

            if i == 8:

                if not self.skip_step_table_surfacecover():
                    self.layer_intersected_dissolved = self.table_canopy_cover.join_data(self.layer_intersected_dissolved)

                if not self.skip_step_table_roughness():
                    self.table_roughness.add_data(self.layer_intersected_dissolved)

                else:

                    i += 1

            if i == 9:

                if not self.skip_step_table_roughness():
                    self.layer_intersected_dissolved = self.table_roughness.join_data(self.layer_intersected_dissolved)

                self.table_erodibility.add_data(self.layer_intersected_dissolved)

            if i == 10:

                self.layer_intersected_dissolved = self.table_erodibility.join_data(self.layer_intersected_dissolved)

                self.table_skinfactor.add_data(self.layer_intersected_dissolved)

            if i == 11:

                self.layer_intersected_dissolved = self.table_skinfactor.join_data(self.layer_intersected_dissolved)

            if i == 12:

                # if there are some values already existing, delete them

                if not len(self.poly_nr_additons) == 0:

                    fids_to_delete = []

                    for fid_value, poly_id in self.poly_nr_additons:

                        fids_to_delete.append(fid_value)

                    delete_features_with_values(self.layer_intersected_dissolved,
                                                TextConstants.field_name_fid,
                                                fids_to_delete)

                    self.poly_nr_additons = []

                # add "POLY_NR" field

                add_fid_field(self.layer_intersected_dissolved)

                # solve raster and raster additions

                self.layer_raster_rasterized = rasterize_layer_by_example(self.layer_intersected_dissolved,
                                                                          TextConstants.field_name_fid,
                                                                          self.layer_raster_dtm,
                                                                          progress_bar=self.progressBar)

                if 0 < len(self.layer_channel_elements_cb.currentText()):
                    value = max_value_in_field(self.layer_intersected_dissolved,
                                               TextConstants.field_name_fid)

                    value = int(value + 1)

                    self.poly_nr_additons.append((value, "channel_elements"))

                    add_field_with_constant_value(self.layer_channel_elements,
                                                  TextConstants.field_name_fid,
                                                  value)

                    raster = rasterize_layer_by_example(self.layer_channel_elements,
                                                        TextConstants.field_name_fid,
                                                        self.layer_raster_dtm,
                                                        progress_bar=self.progressBar)

                    self.layer_raster_rasterized = replace_raster_values_by_raster(self.layer_raster_rasterized,
                                                                                   raster,
                                                                                   progress_bar=self.progressBar)

                if 0 < len(self.layer_drain_elements_cb.currentText()):

                    value = max_value_in_field(self.layer_intersected_dissolved,
                                               TextConstants.field_name_fid)

                    value += 1

                    if 0 < len(self.poly_nr_additons):
                        value = self.poly_nr_additons[-1]
                        value = int(value[0] + 1)

                    self.poly_nr_additons.append((value, "drain_elements"))

                    add_field_with_constant_value(self.layer_drain_elements,
                                                  TextConstants.field_name_fid,
                                                  value)

                    raster = rasterize_layer_by_example(self.layer_drain_elements,
                                                        TextConstants.field_name_fid,
                                                        self.layer_raster_dtm,
                                                        progress_bar=self.progressBar)

                    self.layer_raster_rasterized = replace_raster_values_by_raster(self.layer_raster_rasterized,
                                                                                   raster,
                                                                                   progress_bar=self.progressBar)

                self.progressBar.setMaximum(5)

                # add rows for channel elements and drain elements
                for fid_value, poly_id in self.poly_nr_additons:

                    values = {TextConstants.field_name_fid: fid_value,
                              TextConstants.field_name_init_moisture: 0.0,
                              TextConstants.field_name_poly_id: poly_id}

                    values.update(DEFAULT_EXPORT_VALUES)

                    add_row_without_geom(self.layer_intersected_dissolved, values)

                self.progressBar.setValue(2)

                add_field_with_constant_value(self.layer_intersected_dissolved,
                                              TextConstants.field_name_layer_id,
                                              0)

                add_field_with_constant_value(self.layer_intersected_dissolved,
                                              TextConstants.field_name_layer_thick,
                                              10000)

                self.progressBar.setValue(3)

                self.table_edit_values.add_data(self.layer_intersected_dissolved)

                self.progressBar.setValue(5)

            if i == 13:

                if self.layer_pour_points and self.field_pour_points_cb.currentText():

                    self.layer_pour_points_rasterized = rasterize_layer_by_example(self.layer_pour_points,
                                                                                   self.field_pour_points_cb.currentText(),
                                                                                   self.layer_raster_dtm,
                                                                                   progress_bar=self.progressBar)

                    self.lineEdit_pour_points_raster.setEnabled(True)
                    self.toolButton_pour_points_raster.setEnabled(True)

                # self.table_edit_values.update_values_in_layer(self.layer_intersected_dissolved)

                self.ok_result_layer, msg = evaluate_result_layer(self.layer_intersected_dissolved)

                self.label_data_status.setText(msg)

                if self.ok_result_layer:
                    self.label_data_status.setStyleSheet("color : black;")
                else:
                    self.label_data_status.setStyleSheet("color : red;")

                self.layer_export_parameters = retain_only_fields(self.layer_intersected_dissolved,
                                                                  [TextConstants.field_name_poly_id,
                                                                   TextConstants.field_name_layer_id,
                                                                   TextConstants.field_name_layer_thick,
                                                                   TextConstants.field_name_FT,
                                                                   TextConstants.field_name_MT,
                                                                   TextConstants.field_name_GT,
                                                                   TextConstants.field_name_FU,
                                                                   TextConstants.field_name_MU,
                                                                   TextConstants.field_name_GU,
                                                                   TextConstants.field_name_FS,
                                                                   TextConstants.field_name_GS,
                                                                   TextConstants.field_name_MS,
                                                                   TextConstants.field_name_bulk_density,
                                                                   TextConstants.field_name_corg,
                                                                   TextConstants.field_name_init_moisture,
                                                                   TextConstants.field_name_roughness,
                                                                   TextConstants.field_name_canopy_cover,
                                                                   TextConstants.field_name_skinfactor,
                                                                   TextConstants.field_name_erodibility],
                                                                  "parameters")

                self.layer_export_lookup = retain_only_fields(self.layer_intersected_dissolved,
                                                              [TextConstants.field_name_poly_id,
                                                               TextConstants.field_name_fid],
                                                              "lookup")

            if i + 1 == self.stackedWidget.count() - 1:

                if self.ok_result_layer or self.checkbox_export_empty_data.isChecked():
                    self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

                self.next_pb.setVisible(False)

            if ok:
                self.stackedWidget.setCurrentIndex(i + 1)
                self.progressBar.setMaximum(1)
                self.progressBar.setValue(1)
            else:
                QtWidgets.QMessageBox.warning(self, TextConstants.msg_title, msg)
                self.progressBar.setMaximum(1)
                self.progressBar.setValue(1)

    def prev(self):

        i = self.stackedWidget.currentIndex()

        if i == 3:
            self.layer_soil = self.layer_soil_input
            self.update_layer_soil()

        if i == 5:
            # TODO make sure this makes sense!!!!!!
            # TODO make sure this makes sense!!!!!!
            # TODO make sure this makes sense!!!!!!
            # TODO make sure this makes sense!!!!!!
            self.layer_landuse = self.layer_landuse_interstep
            self.layer_soil = self.layer_soil_interstep

        if self.skip_step_table_roughness() and i == self.roughness_widget_index + 1:
            i = i - 1

        if self.skip_step_table_surfacecover() and i == self.canopycover_widget_index + 1:
            i = i - 1

        if self.skip_step_table_bulkdensity() and i == self.bulkdensity_widget_index + 1:
            i = i - 1

        if self.skip_step_table_corg() and i == self.corg_widget_index + 1:
            i = i - 1

        self.stackedWidget.setCurrentIndex(i - 1)

        if i != self.stackedWidget.count() - 1:
            self.next_pb.setText(TextConstants.text_next)

        self.next_pb.setVisible(True)
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

    def skip_step_table_bulkdensity(self) -> bool:

        return 0 < len(self.fcb_bulk_density.currentText())

    def skip_step_table_corg(self) -> bool:

        return 0 < len(self.fcb_corg.currentText())

    def skip_step_table_roughness(self) -> bool:

        return 0 < len(self.fcb_roughness.currentText())

    def skip_step_table_surfacecover(self) -> bool:

        return 0 < len(self.fcb_surface_cover.currentText())

    @staticmethod
    def cb_unique_values(combo_boxes: List[QtWidgets.QComboBox]) -> int:

        l = []

        for combo_box in combo_boxes:
            if combo_box.currentText() != "":
                l.append(combo_box.currentText())

        return len(set(l))

    @staticmethod
    def cb_number_empty(combo_boxes: List[QtWidgets.QComboBox]) -> int:

        empty = 0

        for combo_box in combo_boxes:
            if combo_box.currentText() == "":
                empty += 1

        return empty
