# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List, NoReturn

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (QComboBox,
                                 QLabel,
                                 QDialog,
                                 QPushButton,
                                 QCalendarWidget,
                                 QLineEdit,
                                 QCheckBox,
                                 QFileDialog,
                                 QDialogButtonBox,
                                 QStackedWidget,
                                 QProgressBar,
                                 QWidget,
                                 QMessageBox)

from qgis.gui import (QgsMapLayerComboBox,
                      QgsFieldComboBox)
from qgis.core import (QgsMapLayerProxyModel,
                       QgsFields,
                       QgsFieldProxyModel,
                       QgsProject,
                       QgsFileUtils,
                       QgsProcessingUtils,
                       QgsRasterLayer)

from .e3d_wizard_process import E3DWizardProcess
from .algorithms.algs import (validate_KA5)
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

from .constants import TextConstants


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
path_ui = Path(__file__).parent / "ui" / "main_wizard_dialog_base.ui"
FORM_CLASS, _ = uic.loadUiType(str(path_ui))


class MainPluginDialog(QDialog, FORM_CLASS):

    landuse_select_widget_index = 4
    corg_widget_index = 6
    bulkdensity_widget_index = corg_widget_index + 1
    canopycover_widget_index = corg_widget_index + 2
    roughness_widget_index = corg_widget_index + 3

    qlabel_main: QLabel
    qlabel_step_description: QLabel
    qlabel_steps: QLabel

    next_pb: QPushButton

    # widget0
    layer_soil_cb: QgsMapLayerComboBox
    layer_landuse_cb: QgsMapLayerComboBox
    raster_dtm_cb: QgsMapLayerComboBox
    calendar: QCalendarWidget

    # widget1
    field_ka5_cb: QgsFieldComboBox
    label_ka5_class: QLabel
    label_soil_id: QLabel
    field_soilid_cb: QgsFieldComboBox

    # widget2
    layer_soil_cb_2: QgsMapLayerComboBox
    le_field_gb: QLineEdit
    le_field_d90: QLineEdit
    cb_addD90: QCheckBox

    # widget 3
    fcb_ftc: QComboBox
    fcb_mtc: QComboBox
    fcb_gtc: QComboBox
    fcb_fuc: QComboBox
    fcb_muc: QComboBox
    fcb_guc: QComboBox
    fcb_fsc: QComboBox
    fcb_msc: QComboBox
    fcb_gsc: QComboBox

    # widget 4
    fcb_landuse: QgsFieldComboBox
    fcb_crop: QgsFieldComboBox

    # widget 6
    label_data_status: QLabel

    # widget initmoisture
    label_initmoisture_layer: QLabel
    label_initmoisture_field: QLabel
    fcb_initmoisture: QgsFieldComboBox
    fcb_initmoisture_layer: QComboBox

    label_bulk_density_layer: QLabel
    label_bulk_density_field: QLabel
    fcb_bulk_density_layer: QComboBox
    fcb_bulk_density: QgsFieldComboBox

    label_corg_layer: QLabel
    label_corg_field: QLabel
    fcb_corg_layer: QComboBox
    fcb_corg: QgsFieldComboBox

    label_roughness_layer: QLabel
    label_roughness_field: QLabel
    fcb_roughness_layer: QComboBox
    fcb_roughness: QgsFieldComboBox

    label_surface_cover_layer: QLabel
    label_surface_cover_field: QLabel
    fcb_surface_cover_layer: QComboBox
    fcb_surface_cover: QgsFieldComboBox

    # widget optional
    layer_channel_elements_cb: QgsMapLayerComboBox
    layer_drain_elements_cb: QgsMapLayerComboBox
    layer_pour_points_cb: QgsMapLayerComboBox

    label_channel_elements: QLabel
    label_drain_elements: QLabel
    label_pour_points: QLabel

    # widget last

    label_landuse_raster: QLabel
    lineEdit_landuse_raster: QLineEdit
    toolButton_landuse_raster: QFileDialog

    label_parameter_table: QLabel
    lineEdit_parameter_table: QLineEdit
    toolButton_parameter_table: QFileDialog

    label_lookup_table: QLabel
    lineEdit_lookup_table: QLineEdit
    toolButton_lookup_table: QFileDialog

    label_pour_points_raster: QLabel
    lineEdit_pour_points_raster: QLineEdit
    toolButton_pour_points_raster: QFileDialog

    label_dem: QLabel
    lineEdit_dem: QLineEdit
    toolButton_dem: QFileDialog

    # main window
    stackedWidget: QStackedWidget
    progressBar: QProgressBar
    button_box: QDialogButtonBox
    checkbox_export_empty_data: QCheckBox

    label_created: QLabel
    label_project: QLabel

    ok_result_layer: bool

    table_bulk_density: TableWidgetBulkDensity
    table_corg: TableWidgetCorg
    table_canopy_cover: TableWidgetCanopyCover
    table_roughness: TableWidgetRoughness
    table_erodibility: TableWidgetErodibility
    table_skinfactor: TableWidgetSkinFactor

    table_edit_values: TableWidgetEditNumericValues

    field_pour_points_cb: QgsFieldComboBox

    # lineEdit_soil_layer: QtWidgets.QLineEdit
    # toolButton_soil_layer: QtWidgets.QToolButton

    label_data_status_confirm: QLabel
    checkbox_export_empty_data: QCheckBox

    e3d_wizard_process: E3DWizardProcess

    def __init__(self, iface, parent=None):

        super(MainPluginDialog, self).__init__(parent)

        self.iface = iface

        self.e3d_wizard_process = E3DWizardProcess()

        self.ok_result_layer = False

        self.setupUi(self)

        self.setWindowTitle(TextConstants.plugin_main_window_name)

        self.stackedWidget.setCurrentIndex(0)

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

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

        self.layer_channel_elements_cb.setFilters(QgsMapLayerProxyModel.RasterLayer)
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
        self.toolButton_dem.clicked.connect(self.select_file_dem)

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
        widget: QWidget = self.stackedWidget.widget(self.landuse_select_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.landuse_select_widget_index, self.table_landuse_assign_catalog)

        self.create_table_corg()

        self.create_table_bulk_density()

        self.create_table_canopy_cover()

        self.create_table_rougness()

        self.create_table_erodibility()

        self.create_table_skinfactor()

        self.table_edit_values = TableWidgetEditNumericValues()
        widget = self.stackedWidget.widget(self.corg_widget_index + 7)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.corg_widget_index + 7, self.table_edit_values)

        self.checkbox_export_empty_data.stateChanged.connect(self.allow_ok_button)

    def select_file_dem(self):
        filter = "asc (*.asc)"
        file_name, type = QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_dem.setText(file_name)

    def select_file_pour_points_raster(self):
        filter = "asc (*.asc)"
        file_name, type = QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_pour_points_raster.setText(file_name)

    def select_file_landuse_raster(self):
        filter = "asc (*.asc)"
        file_name, type = QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_landuse_raster.setText(file_name)

    def select_file_lookup_table(self):
        filter = "csv (*.csv)"
        file_name, type = QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_lookup_table.setText(file_name)

    def select_file_parameter_table(self):
        filter = "csv (*.csv)"
        file_name, type = QFileDialog.getSaveFileName(self, 'Select file', filter=filter)
        file_name = QgsFileUtils.addExtensionFromFilter(file_name, filter)
        self.lineEdit_parameter_table.setText(file_name)

    def allow_ok_button(self):
        if self.sender().isChecked() or self.ok_result_layer:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

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

                ok, missing_values = validate_KA5(self.e3d_wizard_process.layer_soil,
                                                  self.field_ka5_cb.currentText())

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

    def validate_rasters(self):

        msg = ""

        status = True

        if self.raster_dtm_cb.currentLayer() and self.layer_channel_elements_cb.currentLayer():

            original_raster = self.raster_dtm_cb.currentLayer()
            compared_raster = self.layer_channel_elements_cb.currentLayer()

            status = original_raster.crs().srsid() == compared_raster.crs().srsid() and \
                     original_raster.height() == compared_raster.height() and \
                     original_raster.width() == compared_raster.width() and \
                     original_raster.extent().toString(4) == compared_raster.extent().toString(4)

            if not status:
                msg = TextConstants.msg_raster_equality

        return status, msg

    def update_layer_channel_elements(self):

        if 0 < len(self.layer_channel_elements_cb.currentText()):

            self.e3d_wizard_process.set_layer_channel_elements(self.layer_channel_elements_cb.currentLayer())

        else:

            self.e3d_wizard_process.set_layer_channel_elements(None)

    def update_layer_drain_elements(self):

        if 0 < len(self.layer_drain_elements_cb.currentText()):

            self.e3d_wizard_process.set_layer_drain_elements(self.layer_drain_elements_cb.currentLayer())

        else:

            self.e3d_wizard_process.set_layer_drain_elements(None)

    def update_layer_pour_points(self):

        if 0 < len(self.layer_pour_points_cb.currentText()):

            self.e3d_wizard_process.set_layer_pour_points(self.layer_pour_points_cb.currentLayer())

            self.field_pour_points_cb.setFields(self.e3d_wizard_process.get_fields_pour_points_layer())
            self.field_pour_points_cb.setCurrentIndex(0)

        else:

            self.e3d_wizard_process.set_layer_pour_points(None)

            self.field_pour_points_cb.setFields(QgsFields())

    def update_month(self):
        self.date_month = self.calendar.selectedDate().month()

    def update_layer_raster_dtm(self):

        if self.raster_dtm_cb.currentLayer():

            self.e3d_wizard_process.set_layer_raster_dtm(self.raster_dtm_cb.currentLayer())

    def update_layer_landuse(self):

        self.e3d_wizard_process.set_layer_landuse(self.layer_landuse_cb.currentLayer())

        if self.layer_landuse_cb.currentLayer():

            fields = self.e3d_wizard_process.get_fields_landuse_layer()

            self.fcb_landuse.setFields(fields)

            if "LandUse" in fields.names():
                self.fcb_landuse.setField("LandUse")

            self.fcb_crop.setFields(fields)

            if "plodina" in fields.names():
                self.fcb_crop.setField("plodina")

    def update_layer_soil(self):

        if self.e3d_wizard_process.layer_soil:

            fields = self.e3d_wizard_process.get_fields_soil_layer()

            if not self.field_soilid_cb.currentText():
                self.field_soilid_cb.setFields(fields)

            if not self.field_ka5_cb.currentText():
                self.field_ka5_cb.setFields(fields)
                self.field_ka5_cb.setField("ka5")

            field_names = self.e3d_wizard_process.get_field_names_soil_layer()

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
    def add_field_names_and_set_selected_back(combo_box: QComboBox,
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

            fields = self.e3d_wizard_process.get_fields_for_layer(self.fcb_bulk_density_layer.currentText())

            self.fcb_bulk_density.setFields(fields)
            self.fcb_bulk_density.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_bulk_density.setCurrentIndex(0)

        else:
            self.fcb_bulk_density.setFields(QgsFields())

    def update_corg_fields(self):

        if 0 < len(self.fcb_corg_layer.currentText()):

            fields = self.e3d_wizard_process.get_fields_for_layer(self.fcb_corg_layer.currentText())

            self.fcb_corg.setFields(fields)
            self.fcb_corg.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_corg.setCurrentIndex(0)

        else:
            self.fcb_corg.setFields(QgsFields())

    def update_roughness_fields(self):

        if 0 < len(self.fcb_roughness_layer.currentText()):

            fields = self.e3d_wizard_process.get_fields_for_layer(self.fcb_roughness_layer.currentText())

            self.fcb_roughness.setFields(fields)
            self.fcb_roughness.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_roughness.setCurrentIndex(0)

        else:
            self.fcb_roughness.setFields(QgsFields())

    def update_surfacecover_fields(self):

        if 0 < len(self.fcb_surface_cover_layer.currentText()):

            fields = self.e3d_wizard_process.get_fields_for_layer(self.fcb_surface_cover_layer.currentText())

            self.fcb_surface_cover.setFields(fields)
            self.fcb_surface_cover.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_surface_cover.setCurrentIndex(0)

        else:
            self.fcb_surface_cover.setFields(QgsFields())

    def update_initmoisture_fields(self):

        if 0 < len(self.fcb_initmoisture_layer.currentText()):

            fields = self.e3d_wizard_process.get_fields_for_layer(self.fcb_initmoisture_layer.currentText())

            self.fcb_initmoisture.setFields(fields)
            self.fcb_initmoisture.setFilters(QgsFieldProxyModel.Numeric)
            self.fcb_initmoisture.setCurrentIndex(0)

        else:
            self.fcb_initmoisture.setFields(QgsFields())

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

                    self.e3d_wizard_process.set_layer_soil(layer=self.layer_soil_cb.currentLayer())

                    self.e3d_wizard_process.set_layer_landuse(layer=self.layer_landuse_cb.currentLayer())

                    self.update_layer_soil()

            if i == 1:

                ok, msg = self.validate_widget_1()

                if self.field_ka5_cb.currentText():

                    self.e3d_wizard_process.join_ka5_2_layer_soil(ka5_field=self.field_ka5_cb.currentText(),
                                                                  progress_bar=self.progressBar)

                    self.update_layer_soil()

                    self.e3d_wizard_process.soil_2_soil_input()

            if i == 2:

                self.e3d_wizard_process.soil_input_2_soil()

                ok, msg = self.validate_widget_2()

                if ok:

                    self.e3d_wizard_process.rename_soil_field_soil_id(field_to_rename=self.field_soilid_cb.currentText())

                    self.progressBar.setMaximum(4)
                    self.progressBar.setValue(1)

                    # this three columns exists so rename them

                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_MT,
                                                                       self.fcb_mtc.currentText())
                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_MU,
                                                                       self.fcb_muc.currentText())
                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_MS,
                                                                       self.fcb_msc.currentText())

                    self.progressBar.setValue(2)

                    # these six columns may or may not be set, so either rename or create with 0 value

                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_FT,
                                                                       self.fcb_ftc.currentText())
                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_GT,
                                                                       self.fcb_gtc.currentText())
                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_FU,
                                                                       self.fcb_fuc.currentText())
                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_GU,
                                                                       self.fcb_guc.currentText())
                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_FS,
                                                                       self.fcb_fsc.currentText())
                    self.e3d_wizard_process.handle_particle_size_field(TextConstants.field_name_GS,
                                                                       self.fcb_gsc.currentText())

                    self.progressBar.setValue(3)

                    self.e3d_wizard_process.classify_ka5(self.progressBar)

                    self.progressBar.setValue(4)

            if i == 3:

                ok, msg = self.validate_widget_3()

                if ok:

                    self.e3d_wizard_process.merge_landuse_with_crops(field_name_landuse=self.fcb_landuse.currentText(),
                                                                     field_name_crop=self.fcb_crop.currentText(),
                                                                     progress_bar=self.progressBar)

                    self.e3d_wizard_process.backup_fields_landuse()

                self.table_landuse_assign_catalog.add_data(self.e3d_wizard_process.layer_landuse,
                                                           TextConstants.field_name_landuse_crops)

            if i == 4:

                ok = True

                if ok:

                    table = self.table_landuse_assign_catalog.get_data_as_layer(TextConstants.field_name_landuse_crops)

                    self.e3d_wizard_process.join_catalog_info_layer_landuse(table,
                                                                            self.progressBar)

                    self.update_value_layers()

                    self.e3d_wizard_process.backup_input_layers()

            if i == 5:

                self.e3d_wizard_process.restore_input_layers()

                self.e3d_wizard_process.rename_initmoisture(layer_name=self.fcb_initmoisture_layer.currentText(),
                                                            field_name=self.fcb_initmoisture.currentText())

                if self.skip_step_table_corg():

                    self.e3d_wizard_process.rename_corg(layer_name=self.fcb_corg_layer.currentText(),
                                                        field_name=self.fcb_corg.currentText())

                if self.skip_step_table_bulkdensity():

                    self.e3d_wizard_process.rename_bulkdensity(layer_name=self.fcb_bulk_density_layer.currentText(),
                                                               field_name=self.fcb_bulk_density.currentText())

                if self.skip_step_table_roughness():

                    self.e3d_wizard_process.rename_roughness(layer_name=self.fcb_roughness_layer.currentText(),
                                                             field_name=self.fcb_roughness.currentText())

                if self.skip_step_table_surfacecover():

                    self.e3d_wizard_process.rename_cover(layer_name=self.fcb_surface_cover_layer.currentText(),
                                                         field_name=self.fcb_surface_cover.currentText())

                self.e3d_wizard_process.create_main_layer(self.progressBar)

                if self.table_landuse_assign_catalog.data_changes():

                    self.e3d_wizard_process.adjust_search_values(self.table_landuse_assign_catalog.get_data_change_approaches())

                    self.create_table_corg()
                    self.create_table_bulk_density()
                    self.create_table_canopy_cover()
                    self.create_table_rougness()
                    self.create_table_erodibility()
                    self.create_table_skinfactor()

                self.e3d_wizard_process.add_month_field(self.date_month)

                if not self.skip_step_table_corg():
                    self.table_corg.add_data(self.e3d_wizard_process.layer_main)

                else:

                    i += 1

            if i == 6:

                if not self.skip_step_table_corg():
                    self.e3d_wizard_process.layer_main = self.table_corg.join_data(self.e3d_wizard_process.layer_main)

                if not self.skip_step_table_bulkdensity():
                    self.table_bulk_density.add_data(self.e3d_wizard_process.layer_main)

                else:

                    i += 1

            if i == 7:

                if not self.skip_step_table_bulkdensity():
                    self.e3d_wizard_process.layer_main = self.table_bulk_density.join_data(self.e3d_wizard_process.layer_main)

                if not self.skip_step_table_surfacecover():
                    self.table_canopy_cover.add_data(self.e3d_wizard_process.layer_main)

                else:

                    i += 1

            if i == 8:

                if not self.skip_step_table_surfacecover():
                    self.e3d_wizard_process.layer_main = self.table_canopy_cover.join_data(self.e3d_wizard_process.layer_main)

                if not self.skip_step_table_roughness():
                    self.table_roughness.add_data(self.e3d_wizard_process.layer_main)

                else:

                    i += 1

            if i == 9:

                if not self.skip_step_table_roughness():
                    self.e3d_wizard_process.layer_main = self.table_roughness.join_data(self.e3d_wizard_process.layer_main)

                self.table_erodibility.add_data(self.e3d_wizard_process.layer_main)

            if i == 10:

                self.e3d_wizard_process.layer_main = self.table_erodibility.join_data(self.e3d_wizard_process.layer_main)

                self.table_skinfactor.add_data(self.e3d_wizard_process.layer_main)

            if i == 11:

                self.e3d_wizard_process.layer_main = self.table_skinfactor.join_data(self.e3d_wizard_process.layer_main)

            if i == 12:

                ok, msg = self.validate_rasters()

                if ok:

                    # if there are some values already existing, delete them
                    self.e3d_wizard_process.remove_additions_fids_if_exist()

                    # add "POLY_NR" field

                    self.e3d_wizard_process.add_fid_field()

                    # solve raster and raster additions

                    self.e3d_wizard_process.rasterize_main_layer(self.progressBar)

                    self.e3d_wizard_process.add_channel_elements()

                    self.e3d_wizard_process.add_drain_elements()

                    self.progressBar.setMaximum(5)

                    self.e3d_wizard_process.add_poly_nr_rows()

                    self.progressBar.setValue(2)

                    self.e3d_wizard_process.add_fields_contant()

                    self.progressBar.setValue(3)

                    self.table_edit_values.add_data(self.e3d_wizard_process.layer_main)

                    self.progressBar.setValue(5)

            if i == 13:

                self.progressBar.setMaximum(5)

                self.prepare_layer_pour_points()

                self.progressBar.setValue(1)

                self.e3d_wizard_process.prepare_layer_parameters()

                self.progressBar.setValue(2)

                self.evaluate_result_layer_set_message()

                self.progressBar.setValue(3)

                self.e3d_wizard_process.prepare_layer_lookup()

                self.progressBar.setValue(4)

                self.e3d_wizard_process.prepare_layer_e3d()

                self.progressBar.setValue(5)

            if i + 1 == self.stackedWidget.count() - 1:

                if self.ok_result_layer or self.checkbox_export_empty_data.isChecked():
                    self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)

                self.next_pb.setVisible(False)

            if ok:
                self.stackedWidget.setCurrentIndex(i + 1)
                self.progressBar.setMaximum(1)
                self.progressBar.setValue(1)
            else:
                QMessageBox.warning(self, TextConstants.msg_title, msg)
                self.progressBar.setMaximum(1)
                self.progressBar.setValue(1)

    def prev(self):

        i = self.stackedWidget.currentIndex()

        if i == 3:
            self.e3d_wizard_process.soil_input_2_soil()
            self.update_layer_soil()

        if i == 5:
            # TODO make sure this makes sense!!!!!!
            # TODO make sure this makes sense!!!!!!
            # TODO make sure this makes sense!!!!!!
            # TODO make sure this makes sense!!!!!!
            self.e3d_wizard_process.restore_input_layers()

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
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

    def skip_step_table_bulkdensity(self) -> bool:

        return 0 < len(self.fcb_bulk_density.currentText())

    def skip_step_table_corg(self) -> bool:

        return 0 < len(self.fcb_corg.currentText())

    def skip_step_table_roughness(self) -> bool:

        return 0 < len(self.fcb_roughness.currentText())

    def skip_step_table_surfacecover(self) -> bool:

        return 0 < len(self.fcb_surface_cover.currentText())

    @staticmethod
    def cb_unique_values(combo_boxes: List[QComboBox]) -> int:

        l = []

        for combo_box in combo_boxes:
            if combo_box.currentText() != "":
                l.append(combo_box.currentText())

        return len(set(l))

    @staticmethod
    def cb_number_empty(combo_boxes: List[QComboBox]) -> int:

        empty = 0

        for combo_box in combo_boxes:
            if combo_box.currentText() == "":
                empty += 1

        return empty

    def prepare_layer_pour_points(self):

        if self.layer_pour_points_cb.currentLayer() and self.field_pour_points_cb.currentText():

            self.e3d_wizard_process.prepare_pour_points(field_name=self.field_pour_points_cb.currentText())

            self.lineEdit_pour_points_raster.setEnabled(True)
            self.toolButton_pour_points_raster.setEnabled(True)

    def evaluate_result_layer_set_message(self):

        self.ok_result_layer, msg = evaluate_result_layer(self.e3d_wizard_process.layer_parameters)

        self.label_data_status.setText(msg)

        if self.ok_result_layer:
            self.label_data_status.setStyleSheet("color : black;")
            self.label_data_status_confirm.hide()
            self.checkbox_export_empty_data.hide()
        else:
            self.label_data_status.setStyleSheet("color : red;")
            self.label_data_status_confirm.show()
            self.checkbox_export_empty_data.show()

    def create_table_corg(self):
        self.table_corg = TableWidgetCorg(TextConstants.header_table_corg)
        widget = self.stackedWidget.widget(self.corg_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.corg_widget_index, self.table_corg)

    def create_table_bulk_density(self):
        self.table_bulk_density = TableWidgetBulkDensity(TextConstants.header_table_bulkdensity)
        widget = self.stackedWidget.widget(self.bulkdensity_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.bulkdensity_widget_index, self.table_bulk_density)

    def create_table_canopy_cover(self):
        self.table_canopy_cover = TableWidgetCanopyCover(TextConstants.header_table_canopycover)
        widget = self.stackedWidget.widget(self.canopycover_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.canopycover_widget_index, self.table_canopy_cover)

    def create_table_rougness(self):
        self.table_roughness = TableWidgetRoughness(TextConstants.header_table_roughness)
        widget = self.stackedWidget.widget(self.roughness_widget_index)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.roughness_widget_index, self.table_roughness)

    def create_table_erodibility(self):
        self.table_erodibility = TableWidgetErodibility(TextConstants.header_table_erodibility)
        widget = self.stackedWidget.widget(self.corg_widget_index+4)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.corg_widget_index + 4, self.table_erodibility)

    def create_table_skinfactor(self):
        self.table_skinfactor = TableWidgetSkinFactor(TextConstants.header_table_skinfactor)
        widget = self.stackedWidget.widget(self.corg_widget_index+5)
        self.stackedWidget.removeWidget(widget)
        self.stackedWidget.insertWidget(self.corg_widget_index + 5, self.table_skinfactor)
