from qgis.PyQt.QtCore import (QRunnable,
                              QObject,
                              pyqtSignal,
                              pyqtSlot)

from qgis.core import (QgsVectorLayer,
                       QgsRasterLayer,
                       QgsVectorFileWriter,
                       QgsCoordinateTransformContext)

from ..algorithms.algs import save_raster_as_asc


class ExportWorker(QRunnable):
    steps = 4

    def __init__(self):

        super(ExportWorker, self).__init__()

        self.signals = WorkerSignals()

        self.layer_lookup = None
        self.path_layer_lookup = None

        self.layer_parameters = None
        self.path_layer_parameters = None

        self.layer_raster_rasterized = None
        self.path_raster_rasterized = None

        self.layer_pour_points_rasterized = None
        self.path_pour_points = None

    def set_export_lookup(self,
                          layer_lookup: QgsVectorLayer,
                          path_layer_lookup: str):
        self.layer_lookup = layer_lookup
        self.path_layer_lookup = path_layer_lookup

    def set_export_parameters(self,
                              layer_parameters: QgsVectorLayer,
                              path_layer_parameters: str):
        self.layer_parameters = layer_parameters
        self.path_layer_parameters = path_layer_parameters

    def set_export_rasterized(self,
                              layer_raster_rasterized: QgsRasterLayer,
                              path_raster_rasterized: str):
        self.layer_raster_rasterized = layer_raster_rasterized
        self.path_raster_rasterized = path_raster_rasterized

    def set_export_pour_points(self,
                               layer_pour_points_rasterized: QgsRasterLayer,
                               path_pour_points: str):
        self.layer_pour_points_rasterized = layer_pour_points_rasterized
        self.path_pour_points = path_pour_points

    @pyqtSlot()
    def run(self):

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "CSV"
        options.fileEncoding = "UTF-8"
        options.layerOptions = ["STRING_QUOTING=IF_NEEDED"]

        QgsVectorFileWriter.writeAsVectorFormatV2(self.layer_lookup,
                                                  self.path_layer_lookup,
                                                  transformContext=QgsCoordinateTransformContext(),
                                                  options=options)

        self.signals.progress.emit(1)

        QgsVectorFileWriter.writeAsVectorFormatV2(self.layer_parameters,
                                                  self.path_layer_parameters,
                                                  transformContext=QgsCoordinateTransformContext(),
                                                  options=options)

        self.signals.progress.emit(2)

        if self.layer_raster_rasterized:
            save_raster_as_asc(self.layer_raster_rasterized,
                               self.path_raster_rasterized)

        self.signals.progress.emit(3)

        if self.layer_pour_points_rasterized and self.path_pour_points:
            save_raster_as_asc(self.layer_pour_points_rasterized,
                               self.path_raster_rasterized)

        self.signals.progress.emit(4)

        self.signals.result.emit()


class WorkerSignals(QObject):
    result = pyqtSignal()
    progress = pyqtSignal(int)
