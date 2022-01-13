# -*- coding: utf-8 -*-
from pathlib import Path

from qgis.PyQt.QtCore import (QSettings,
                              QTranslator,
                              QCoreApplication,
                              QThreadPool)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from qgis.core import (QgsApplication,
                       Qgis)

from qgis.gui import (QgisInterface)

import processing

from .export.export_worker import ExportWorker
from .constants import TextConstants
from .algorithms.utils import add_maplayer_to_project

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .main_plugin_window import MainPluginDialog
from .gui_classes.dialog_result import DialogResult
from .gui_classes.dialog_empty_data import DialogEmptyData
from .gui_classes.dialog_import_data_with_style import DialogLoadResult
from .gui_classes.dialog_about import DialogAbout
import os.path
import sys

from .erosion_data_plugin_provider import ErosionDataPluginProvider


class ErosionDataPreparationPlugin:

    garbrech_roughness_action: QAction

    dlg: MainPluginDialog

    dialog: DialogResult

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface: QgisInterface = iface

        self.dlg = None

        self.threadpool = QThreadPool()

        # initialize plugin directory
        self.path_plugin = Path(__file__).parent
        self.plugin_dir = str(self.path_plugin)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'guitests_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions_menu_toolbar = []

        # Declare instance attributes
        self.actions = []
        self.menu = TextConstants.plugin_name

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.provider = ErosionDataPluginProvider()

        self.toolbar = self.iface.addToolBar(TextConstants.plugin_toolbar_name)
        self.toolbar.setObjectName(TextConstants.plugin_toolbar_name_id)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('guitests', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        add_to_specific_toolbar=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        if add_to_specific_toolbar:
            add_to_specific_toolbar.addAction(action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        path_icon = Path(__file__).parent / "icon.png"

        self.first_start = True

        QgsApplication.processingRegistry().addProvider(self.provider)

        self.add_action(icon_path=str(self.path_plugin / "icons" / "main.png"),
                        text=TextConstants.plugin_main_window_name,
                        callback=self.run,
                        add_to_toolbar=True,
                        add_to_menu=TextConstants.plugin_name,
                        add_to_specific_toolbar=self.toolbar)

        self.add_action(icon_path=str(self.path_plugin / "icons" / "reset_wizard.png"),
                        text=TextConstants.plugin_action_name_empty_wizard,
                        callback=self.reset_progress,
                        add_to_toolbar=False,
                        add_to_specific_toolbar=self.toolbar)

        self.add_action(icon_path=str(self.path_plugin / "icons" / "results_to_project.png"),
                        text=TextConstants.plugin_action_name_load_data,
                        callback=self.load_result,
                        add_to_toolbar=False,
                        add_to_specific_toolbar=self.toolbar)

        self.add_action(icon_path=str(self.path_plugin / "icons" / "roughness.png"),
                        text=TextConstants.plugin_action_name_garbrech_roughness,
                        callback=self.GarbrechRoughnessTool,
                        add_to_toolbar=False,
                        add_to_specific_toolbar=self.toolbar)

        self.add_action(icon_path=str(self.path_plugin / "icons" / "convert_pourpoint_data.png"),
                        text=TextConstants.plugin_action_name_process_pour_points,
                        callback=self.ProcessPourPoint,
                        add_to_toolbar=False,
                        add_to_specific_toolbar=self.toolbar)

        self.add_action(icon_path=str(self.path_plugin / "icons" / "info.png"),
                        text=TextConstants.dialog_about_header,
                        callback=self.show_about,
                        add_to_toolbar=False,
                        add_to_specific_toolbar=self.toolbar)

    def ProcessPourPoint(self):
        tool_call = f"{TextConstants.tool_group_id}:{TextConstants.plugin_action_id_process_pour_points}"
        processing.execAlgorithmDialog(tool_call, {})

    def GarbrechRoughnessTool(self):
        tool_call = f"{TextConstants.tool_group_id}:{TextConstants.plugin_action_id_garbrech_roughness}"
        processing.execAlgorithmDialog(tool_call, {})

    def reset_progress(self):

        dialog_empty = DialogEmptyData(self.iface.mainWindow())

        dialog_empty.show()

        result = dialog_empty.exec_()

        if result == QFileDialog.Rejected:
            return

        if result:

            if self.dlg:

                self.dlg.hide()

                self.dlg = MainPluginDialog(self.iface)

                self.iface.messageBar().pushMessage(TextConstants.information_emptied, Qgis.Success)

                return

    def show_about(self):

        dialog_about = DialogAbout(self.iface.mainWindow())

        dialog_about.show()

        result = dialog_about.exec_()

        if result == QFileDialog.Rejected:
            return

        if result:
            return

    def load_result(self):

        dialog_load = DialogLoadResult(self.iface.mainWindow())

        dialog_load.show()

        result = dialog_load.exec_()

        if result == QFileDialog.Rejected:
            return

        if result:

            dialog_load.load_result_data_with_style()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                TextConstants.plugin_name,
                action)
            self.iface.removeToolBarIcon(action)

        for action in self.actions_menu_toolbar:
            self.iface.removePluginMenu(
                TextConstants.plugin_name,
                action)
            self.toolbar.removeAction(action)

        del self.toolbar

        QgsApplication.processingRegistry().removeProvider(self.provider)

    def run(self):
        """Run method that performs all the real work"""

        if self.dlg is None:
            self.dlg = MainPluginDialog(self.iface)

        self.dlg.show()
        result = self.dlg.exec_()
        # See if OK was pressed

        if result == QFileDialog.Rejected:
            return

        if result:

            path_pour_points = None

            if self.dlg.e3d_wizard_process.layer_pour_points_rasterized:
                path_pour_points = self.dlg.lineEdit_pour_points_raster.text()

            add_maplayer_to_project(self.dlg.e3d_wizard_process.layer_e3d)

            self.dialog = DialogResult(path_landuse_raster=self.dlg.lineEdit_landuse_raster.text(),
                                       path_parameter_table=self.dlg.lineEdit_parameter_table.text(),
                                       path_lookup_table=self.dlg.lineEdit_lookup_table.text(),
                                       path_pour_points_raster=path_pour_points,
                                       path_dem=self.dlg.lineEdit_dem.text())

            worker = ExportWorker()

            worker.set_export_lookup(self.dlg.e3d_wizard_process.layer_lookup,
                                     self.dlg.lineEdit_lookup_table.text())

            worker.set_export_parameters(self.dlg.e3d_wizard_process.layer_parameters,
                                         self.dlg.lineEdit_parameter_table.text())

            worker.set_export_rasterized(self.dlg.e3d_wizard_process.layer_main_raster,
                                         self.dlg.lineEdit_landuse_raster.text())

            worker.set_export_pour_points(self.dlg.e3d_wizard_process.layer_pour_points_rasterized,
                                          self.dlg.lineEdit_pour_points_raster.text())

            worker.set_export_dem(self.dlg.e3d_wizard_process.layer_raster_dtm_edited,
                                  self.dlg.lineEdit_dem.text())

            self.dialog.set_progress_bar(worker.steps)

            worker.signals.progress.connect(self.dialog_update_progress)
            worker.signals.result.connect(self.dialog_set_finished)

            self.threadpool.start(worker)

            self.dialog.show()
            self.dialog.exec_()

    def dialog_update_progress(self, value: int):
        self.dialog.update_progress_bar(value)

    def dialog_set_finished(self):
        self.dialog.export_finished()
