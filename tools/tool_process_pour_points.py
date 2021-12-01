from pathlib import Path

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QIcon

from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsFeature,
                       QgsFields,
                       QgsField,
                       QgsProcessingFeedback,
                       QgsVectorLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsFeatureSink,
                       QgsMemoryProviderUtils,
                       QgsWkbTypes,
                       QgsFeatureRequest,
                       QgsVectorLayerUtils,
                       QgsVectorFileWriter,
                       QgsCoordinateTransformContext)

from ..constants import TextConstants


class ProcessPourPointsAlgorithm(QgsProcessingAlgorithm):

    INPUT = "Input"
    TIME = "Time"
    CELLSIZE = "CellSize"
    OUTPUT_AGG = "OutputAgg"
    OUTPUT_UPDATE = "OutputUpdate"
    CALCULATE_RUNOFF = "CalcRunoff"

    field_name_id = "ID"
    field_name_time = "TIME"

    fn_pourPointID = "pourPointID"
    fn_maxFlow_ls = "maxFlow_ls"
    fn_totOutflow_m3 = "totOutflow_m3"
    fn_totSedMass_kg = "totSedMass_kg"
    fn_totClayMass_kg = "totClayMass_kg"
    fn_totSiltMass_kg = "totSiltMass_kg"
    fn_totSandMass_kg = "totSandMass_kg"
    fn_totClayPerc = "totClayPerc"
    fn_totSiltPerc = "totSiltPerc"
    fn_totSandPerc = "totSandPerc"

    fn_runoff_ls = "runoff_ls"
    fn_cumRunoff_m3 = "cumRunoff_m3"
    fn_sedMass_kg = "sedMass_kg"
    fn_clay_kg = "clay_kg"
    fn_silt_kg = "silt_kg"
    fn_sand_kg = "sand_kg"
    fn_clay_perc = "clay_perc"
    fn_silt_perc = "silt_perc"
    fn_sand_perc = "sand_perc"

    headers = ["Date", "Time", "ID", "Row", "Col", "Sedbudget", "Runoff", "Sedvol", "Sedconc", "Clay", "Silt",
               "Totero", "Totdep", "Netero", "ChRunoff", "ChSedvol", "ChNetEro", "ChClay", "ChSilt", "Q_Cell"]

    def createInstance(self):
        return ProcessPourPointsAlgorithm()

    def name(self):
        return TextConstants.plugin_action_id_process_pour_points

    def displayName(self):
        return "Process Pour Points"

    def group(self):
        return TextConstants.tool_group_name

    def groupId(self):
        return TextConstants.tool_group_id

    def shortHelpString(self):
        return "Process Pour Points"

    def icon(self) -> QIcon:
        path = Path(__file__).parent.parent / "icons" / "convert_pourpoint_data.png"
        return QIcon(str(path))

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Input Pour Points CSV file",
                extension="csv")
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TIME,
                "Timestep [s]",
                defaultValue=300
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.CELLSIZE,
                "Raster cell size [m]",
                defaultValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CALCULATE_RUNOFF,
                "Sečíst plošný a soustředěný povrchový odtok",
                defaultValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_AGG,
                "Output aggregated",
                fileFilter="CSV file (*.csv)"
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_UPDATE,
                "Output updated",
                defaultValue="file.csv",
                fileFilter="CSV file (*.csv)"
            )
        )

    def prepare_summary_layer(self) -> QgsVectorLayer:

        fields = QgsFields()
        fields.append(QgsField(self.fn_pourPointID, QVariant.Int))
        fields.append(QgsField(self.fn_maxFlow_ls, QVariant.Double))
        fields.append(QgsField(self.fn_totOutflow_m3, QVariant.Double))
        fields.append(QgsField(self.fn_totSedMass_kg, QVariant.Double))
        fields.append(QgsField(self.fn_totClayMass_kg, QVariant.Double))
        fields.append(QgsField(self.fn_totSiltMass_kg, QVariant.Double))
        fields.append(QgsField(self.fn_totSandMass_kg, QVariant.Double))
        fields.append(QgsField(self.fn_totClayPerc, QVariant.Double))
        fields.append(QgsField(self.fn_totSiltPerc, QVariant.Double))
        fields.append(QgsField(self.fn_totSandPerc, QVariant.Double))

        layer_summary = QgsMemoryProviderUtils.createMemoryLayer("summary_layer",
                                                                 fields,
                                                                 QgsWkbTypes.NoGeometry)

        return layer_summary

    def prepare_updated_layer(self, layer: QgsVectorLayer) -> QgsVectorLayer:

        fields = layer.fields()
        fields.append(QgsField(self.fn_runoff_ls, QVariant.Double))
        fields.append(QgsField(self.fn_cumRunoff_m3, QVariant.Double))
        fields.append(QgsField(self.fn_sedMass_kg, QVariant.Double))
        fields.append(QgsField(self.fn_clay_kg, QVariant.Double))
        fields.append(QgsField(self.fn_silt_kg, QVariant.Double))
        fields.append(QgsField(self.fn_sand_kg, QVariant.Double))
        fields.append(QgsField(self.fn_clay_perc, QVariant.Double))
        fields.append(QgsField(self.fn_silt_perc, QVariant.Double))
        fields.append(QgsField(self.fn_sand_perc, QVariant.Double))

        layer_updated = QgsMemoryProviderUtils.createMemoryLayer(layer.name(),
                                                                 fields,
                                                                 QgsWkbTypes.NoGeometry)

        return layer_updated

    def validate_headers(self, layer: QgsVectorLayer) -> bool:

        fields = layer.fields().names()

        for field in fields:
            if field not in self.headers:
                return False

        return True

    def save_layer_to_file(self, layer: QgsVectorLayer, file_name: str) -> None:

        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.fileEncoding = "UTF-8"
        save_options.driverName = "CSV"
        save_options.layerName = layer.name()

        QgsVectorFileWriter.writeAsVectorFormatV3(layer,
                                                  file_name,
                                                  QgsCoordinateTransformContext(),
                                                  save_options)

    def checkParameterValues(self, parameters, context):

        layer_input: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.INPUT, context)

        if not self.validate_headers(layer_input):
            return False, "Header of csv file does not match requirements."

        return super().checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback: QgsProcessingFeedback):

        layer_input: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.INPUT, context)

        timeStep = self.parameterAsInt(parameters, self.TIME, context)

        cellSize = self.parameterAsInt(parameters, self.CELLSIZE, context)

        calculate_ch_runoff = self.parameterAsBoolean(parameters, self.CALCULATE_RUNOFF, context)

        layer_summarized = self.prepare_summary_layer()

        layer_updated = self.prepare_updated_layer(layer_input)

        path_layer_summary = self.parameterAsFileOutput(parameters, self.OUTPUT_AGG, context)

        path_layer_updated = self.parameterAsFileOutput(parameters, self.OUTPUT_UPDATE, context)

        layer_summarized.startEditing()
        layer_updated.startEditing()

        field_index = layer_input.fields().lookupField(self.field_name_id)

        pp_values = layer_input.uniqueValues(field_index)

        for pp_value in pp_values:

            print(f"---{pp_value}")
            request = QgsFeatureRequest().setFilterExpression(f'"{self.field_name_id}" = {pp_value}')

            orderby = QgsFeatureRequest.OrderBy([QgsFeatureRequest.OrderByClause(self.field_name_time)])

            request.setOrderBy(orderby)

            features = layer_input.getFeatures(request)

            i = 0
            maxFlow_ls = 0
            totOutflow_m3 = 0
            totSedMass_kg = 0
            totClayMass_kg = 0
            totSiltMass_kg = 0
            totSandMass_kg = 0
            totClayPerc = 0
            totSiltPerc = 0
            totSandPerc = 0

            for feature in features:

                # cummulative runoff
                if feature.attribute("ChRunoff") == "-9999.000":
                    cumRunoff = float(feature.attribute("Runoff")) * cellSize
                else:
                    cumRunoff = float(feature.attribute("Runoff")) * cellSize

                    if calculate_ch_runoff:
                        cumRunoff = cumRunoff + float(feature.attribute("ChRunoff")) * cellSize

                if cumRunoff > totOutflow_m3:
                    totOutflow_m3 = cumRunoff

                # runoff in l/s
                if i == 0:
                    runoff = 0.0
                    prevCumRunoff = cumRunoff
                else:
                    runoff = (cumRunoff - prevCumRunoff) / timeStep * 1000
                    prevCumRunoff = cumRunoff
                if runoff > maxFlow_ls:
                    maxFlow_ls = runoff

                # sediment mass in kg
                if feature.attribute("ChSedvol") == "-9999.000":
                    sedMass = float(feature.attribute("Sedvol")) * cellSize
                else:
                    sedMass = float(feature.attribute("Sedvol")) * cellSize

                    if calculate_ch_runoff:
                        sedMass = sedMass + float(feature.attribute("ChSedvol")) * cellSize

                if sedMass > totSedMass_kg:
                    totSedMass_kg = sedMass

                # clay mass in kg
                if feature.attribute("ChSedvol") == "-9999.000":
                    clayMass = float(feature.attribute("Sedvol")) * float(feature.attribute("Clay")) / 100 * cellSize
                else:
                    clayMass = (float(feature.attribute("Sedvol")) * float(feature.attribute("Clay")) / 100 +
                                float(feature.attribute("ChClay"))) * cellSize
                if sedMass > 0:
                    clayPerc = clayMass / sedMass
                else:
                    clayPerc = 0
                if clayMass > totClayMass_kg:
                    totClayMass_kg = clayMass

                # silt mass in kg
                if feature.attribute("ChSedvol") == "-9999.000":
                    siltMass = float(feature.attribute("Sedvol")) * float(feature.attribute("Silt")) / 100 * cellSize
                else:
                    siltMass = (float(feature.attribute("Sedvol")) * float(feature.attribute("Silt")) / 100 +
                                float(feature.attribute("ChSilt"))) * cellSize
                if sedMass > 0:
                    siltPerc = siltMass / sedMass
                else:
                    siltPerc = 0
                if siltMass > totSiltMass_kg:
                    totSiltMass_kg = siltMass

                # sand mass in kg
                if feature.attribute("ChSedvol") == "-9999.000":
                    sandMass = float(feature.attribute("Runoff")) * \
                               (100 - float(feature.attribute("Clay")) -
                                float(feature.attribute("Silt"))) / 100 * cellSize
                else:
                    sandMass = (float(feature.attribute("Runoff")) *
                                (100 - float(feature.attribute("Clay")) - float(feature.attribute("Silt"))) / 100 +
                                (float(feature.attribute("ChSedvol")) - float(feature.attribute("ChClay")) -
                                 float(feature.attribute("ChSilt")))) * cellSize
                if sedMass > 0:
                    sandPerc = sandMass / sedMass
                else:
                    sandPerc = 0
                if sandMass > totSandMass_kg:
                    totSandMass_kg = sandMass

                feature_updated = QgsFeature(feature)

                feature_updated = QgsVectorLayerUtils.makeFeatureCompatible(feature_updated, layer_updated)[0]

                feature_updated.setAttribute(self.fn_runoff_ls, runoff)
                feature_updated.setAttribute(self.fn_cumRunoff_m3, cumRunoff)
                feature_updated.setAttribute(self.fn_sedMass_kg, sedMass)
                feature_updated.setAttribute(self.fn_clay_kg, clayMass)
                feature_updated.setAttribute(self.fn_silt_kg, siltMass)
                feature_updated.setAttribute(self.fn_sand_kg, sandMass)
                feature_updated.setAttribute(self.fn_clay_perc, clayPerc)
                feature_updated.setAttribute(self.fn_silt_perc, siltPerc)
                feature_updated.setAttribute(self.fn_sand_perc, sandPerc)

                layer_updated.addFeature(feature_updated)

                i += 1

            if totSedMass_kg > 0:
                totClayPerc = totClayMass_kg / totSedMass_kg
                totSiltPerc = totSiltMass_kg / totSedMass_kg
                totSandPerc = totSandMass_kg / totSedMass_kg
            else:
                totClayPerc = 0
                totSiltPerc = 0
                totSandPerc = 0

            feature_agg = QgsVectorLayerUtils.createFeature(layer_summarized)

            feature_agg.setAttributes(
                [pp_value, maxFlow_ls, totOutflow_m3, totSedMass_kg, totClayMass_kg, totSiltMass_kg,
                 totSandMass_kg, totClayPerc, totSiltPerc, totSandPerc])

            layer_summarized.addFeature(feature_agg)

        layer_summarized.commitChanges()
        layer_updated.commitChanges()

        self.save_layer_to_file(layer_summarized, path_layer_summary)

        self.save_layer_to_file(layer_updated, path_layer_updated)

        return {}
