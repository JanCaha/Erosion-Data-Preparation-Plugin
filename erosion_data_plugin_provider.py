from pathlib import Path
from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .tools.tool_garbrecht_roughness import GarbrechtRougnessProcessingAlgorithm
from .constants import TextConstants


class ErosionDataPluginProvider(QgsProcessingProvider):

    def unload(self):
        QgsProcessingProvider.unload(self)

    def loadAlgorithms(self):
        self.addAlgorithm(GarbrechtRougnessProcessingAlgorithm())

    def icon(self):
        icon_path = Path(__file__).parent / "icons" / "main.png"
        return QIcon(str(icon_path))

    def id(self):
        return TextConstants.tool_group_id

    def name(self):
        return TextConstants.tool_group_name

    def longName(self):
        return self.name()
