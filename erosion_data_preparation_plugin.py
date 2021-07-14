# -*- coding: utf-8 -*-
from pathlib import Path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from qgis.core import (Qgis, QgsProject, QgsApplication)

import processing

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .main_plugin_window import MainPluginDialog
import os.path

from .erosion_data_plugin_provider import ErosionDataPluginProvider


class ErosionDataPreparationPlugin:

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface

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

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'Erosion-3D Data Preparation')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.provider = ErosionDataPluginProvider()

        self.toolbar = self.iface.addToolBar("Erosion-3D Data Preparation Toolbar")
        self.toolbar.setObjectName('Erosion3DDataPreparationToolbar')

        self.garbrech_roughness_action: QAction

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
        parent=None):

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

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        path_icon = Path(__file__).parent / "icon.png"

        icon_path = str(path_icon.absolute())

        self.add_action(
            icon_path,
            text=self.tr(u'Erosion-3D Data Preparation'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

        QgsApplication.processingRegistry().addProvider(self.provider)

        icon = QIcon(str(self.path_plugin / "icon.png"))
        self.garbrech_roughness_action = QAction(icon, "Garbrech roughness", self.iface.mainWindow())
        self.garbrech_roughness_action.setObjectName('GarbrechRoughness')
        self.garbrech_roughness_action.triggered.connect(self.GarbrechRoughnessTool)
        self.toolbar.addAction(self.garbrech_roughness_action)

    def GarbrechRoughnessTool(self):
        processing.execAlgorithmDialog('erosiondataplugin:GarbrechtRougness', {})

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'Erosion-3D Data Preparation'),
                action)
            self.iface.removeToolBarIcon(action)

        self.iface.removeToolBarIcon(self.garbrech_roughness_action)
        self.GarbrechRoughnessTool = None
        del self.toolbar

        QgsApplication.processingRegistry().removeProvider(self.provider)

    def run(self):
        """Run method that performs all the real work"""

        self.dlg = MainPluginDialog(self.iface)

        self.dlg.show()
        result = self.dlg.exec_()
        # See if OK was pressed

        if result == QFileDialog.Rejected:
            return

        if result:
            # QgsProject.instance().addMapLayer(self.dlg.layer_soil)
            # QgsProject.instance().addMapLayer(self.dlg.layer_landuse)
            QgsProject.instance().addMapLayer(self.dlg.layer_intersected_dissolved)
            # self.iface.messageBar().pushMessage(self.tr('<b>{}</b> reloaded.').format(self.dlg.__dict__.keys()),
            #                                     Qgis.Info)
