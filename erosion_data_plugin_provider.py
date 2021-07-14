from pathlib import Path
from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .tools.tool_garbrecht_roughness import GarbrechtRougnessProcessingAlgorithm


class ErosionDataPluginProvider(QgsProcessingProvider):

    def unload(self):
        QgsProcessingProvider.unload(self)

    def loadAlgorithms(self):
        self.addAlgorithm(GarbrechtRougnessProcessingAlgorithm())

    def icon(self):
        icon_path = Path(__file__).parent / "icon.png"
        return QIcon(str(icon_path))

    def id(self):
        return "erosiondataplugin"

    def name(self):
        return "Erosion-3D Data Plugin"

    def longName(self):
        return self.name()
