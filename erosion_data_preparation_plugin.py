# -*- coding: utf-8 -*-
from pathlib import Path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from qgis.core import (Qgis, QgsProject, QgsApplication, QgsFileUtils, QgsVectorFileWriter, QgsCoordinateTransformContext)
from qgis.gui import (QgisInterface)

import processing

from .algorithms.algs import save_raster_as_asc
from .constants import TextConstants

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .main_plugin_window import MainPluginDialog
import os.path

from .erosion_data_plugin_provider import ErosionDataPluginProvider


class ErosionDataPreparationPlugin:

    garbrech_roughness_action: QAction

    dlg: MainPluginDialog

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface: QgisInterface = iface

        self.dlg = None

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

        self.add_action(icon_path=str(self.path_plugin / "icon.png"),
                        text=TextConstants.plugin_main_tool_name,
                        callback=self.run,
                        add_to_toolbar=True,
                        add_to_menu=TextConstants.plugin_name,
                        add_to_specific_toolbar=self.toolbar)

        self.add_to_pluginmenu_and_toolbar(icon=str(self.path_plugin / "icon.png"),
                                           action_name=TextConstants.plugin_action_name_garbrech_roughness,
                                           action_id=TextConstants.plugin_action_id_garbrech_roughness,
                                           callback=self.GarbrechRoughnessTool,
                                           plugin_menu_name=TextConstants.plugin_name)

    def add_to_pluginmenu_and_toolbar(self,
                                      icon: str,
                                      action_name: str,
                                      action_id: str,
                                      callback,
                                      plugin_menu_name: str):

        icon = QIcon(icon)
        action = QAction(icon, action_name, self.iface.mainWindow())
        action.setObjectName(action_id)
        action.triggered.connect(callback)

        self.toolbar.addAction(action)
        self.iface.addPluginToMenu(plugin_menu_name, action)

        self.actions_menu_toolbar.append(action)

    def GarbrechRoughnessTool(self):
        tool_call = f"{TextConstants.tool_group_id}:{TextConstants.plugin_action_id_garbrech_roughness}"
        processing.execAlgorithmDialog(tool_call, {})

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

            if self.dlg.layer_pour_points_rasterized:
                save_raster_as_asc(self.dlg.layer_pour_points_rasterized,
                                   self.dlg.lineEdit_pour_points_raster.text())

            save_raster_as_asc(self.dlg.layer_raster_rasterized,
                               self.dlg.lineEdit_landuse_raster.text())

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "CSV"
            options.fileEncoding = "UTF-8"

            QgsVectorFileWriter.writeAsVectorFormatV2(self.dlg.layer_export_lookup,
                                                      self.dlg.lineEdit_lookup_table.text(),
                                                      transformContext=QgsCoordinateTransformContext(),
                                                      options=options)

            QgsVectorFileWriter.writeAsVectorFormatV2(self.dlg.layer_export_parameters,
                                                      self.dlg.lineEdit_parameter_table.text(),
                                                      transformContext=QgsCoordinateTransformContext(),
                                                      options=options)
