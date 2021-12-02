from pathlib import Path

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QIcon

from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterVectorLayer,
                       QgsFeature,
                       QgsFields,
                       QgsField,
                       QgsProcessingFeedback,
                       QgsVectorLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsFeatureSink)

from ..constants import TextConstants


class GarbrechtRougnessProcessingAlgorithm(QgsProcessingAlgorithm):

    INPUT = "Input"
    OUTPUT = "Output"
    D90 = "D90"
    D90NAME = "D90NAME"
    NNAME = "NNAME"
    FT = "FT"
    MT = "MT"
    GT = "GT"
    FU = "FU"
    MU = "MU"
    GU = "GU"
    FS = "FS"
    MS = "MS"
    GS = "GS"

    def createInstance(self):
        return GarbrechtRougnessProcessingAlgorithm()

    def name(self):
        return TextConstants.plugin_action_id_garbrech_roughness

    def displayName(self):
        return TextConstants.tool_gb_name

    def group(self):
        return TextConstants.tool_group_name

    def groupId(self):
        return TextConstants.tool_group_id

    def shortHelpString(self):
        return TextConstants.tool_gb_help

    def icon(self) -> QIcon:
        path = Path(__file__).parent.parent / "icons" / "roughness.png"
        return QIcon(str(path))

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                TextConstants.tool_gb_input_layer
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.D90,
                TextConstants.tool_gb_add_d90
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.D90NAME,
                TextConstants.tool_gb_field_d90,
                "d90"
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.NNAME,
                TextConstants.tool_gb_field_gr,
                "N_garbr"
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FT,
                TextConstants.label_FT,
                defaultValue="FT",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.MT,
                TextConstants.label_MT,
                defaultValue="MT",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.GT,
                TextConstants.label_GT,
                defaultValue="GT",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FU,
                TextConstants.label_FU,
                defaultValue="FU",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.MU,
                TextConstants.label_MU,
                defaultValue="MU",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.GU,
                TextConstants.label_GU,
                defaultValue="GU",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FS,
                TextConstants.label_FS,
                defaultValue="FS",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.MS,
                TextConstants.label_MS,
                defaultValue="MS",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.GS,
                TextConstants.label_GS,
                defaultValue="GS",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                TextConstants.tool_gb_output
            )
        )

    def processAlgorithm(self, parameters, context, feedback: QgsProcessingFeedback):

        att_ft = self.parameterAsString(parameters, self.FT, context)
        att_mt = self.parameterAsString(parameters, self.MT, context)
        att_gt = self.parameterAsString(parameters, self.GT, context)
        att_fu = self.parameterAsString(parameters, self.FU, context)
        att_mu = self.parameterAsString(parameters, self.MU, context)
        att_gu = self.parameterAsString(parameters, self.GU, context)
        att_fs = self.parameterAsString(parameters, self.FS, context)
        att_ms = self.parameterAsString(parameters, self.MS, context)
        att_gs = self.parameterAsString(parameters, self.GS, context)

        # default field names of the fractions content
        FTcode = "FT"
        MTcode = "MT"
        GTcode = "GT"
        FUcode = "FU"
        MUcode = "MU"
        GUcode = "GU"
        FScode = "FS"
        MScode = "MS"
        GScode = "GS"
        # array of fraction codes - needed for iterating the fractions in right order
        fractionCodes = [FTcode, MTcode, GTcode, FUcode, MUcode, GUcode, FScode, MScode, GScode]
        # dictionary of the fractions classes codes and particle diameter of top and bottom bodred value
        top = "top"
        bot = "bottom"
        fractions = {FTcode: {bot: 0.0, top: 0.0002},
                     MTcode: {bot: 0.0002, top: 0.00063},
                     GTcode: {bot: 0.00063, top: 0.002},
                     FUcode: {bot: 0.002, top: 0.0063},
                     MUcode: {bot: 0.0063, top: 0.02},
                     GUcode: {bot: 0.02, top: 0.063},
                     FScode: {bot: 0.063, top: 0.2},
                     MScode: {bot: 0.2, top: 0.63},
                     GScode: {bot: 0.63, top: 2.0}}

        layer_input: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.INPUT, context)

        add_d90 = self.parameterAsBoolean(parameters, self.D90, context)

        field_name_d90 = self.parameterAsString(parameters, self.D90NAME, context)
        field_name_gb = self.parameterAsString(parameters, self.NNAME, context)

        total = 100.0 / layer_input.dataProvider().featureCount() if layer_input.dataProvider().featureCount() else 0

        layer_input.startEditing()

        feature_polygon: QgsFeature

        add_fields = QgsFields()
        add_fields.append(QgsField(field_name_gb, QVariant.Double))

        if add_d90:
            add_fields.append(QgsField(field_name_d90, QVariant.Double))

        fields: QgsFields = layer_input.fields()

        fields.append(QgsField(field_name_gb, QVariant.Double))

        if add_d90:
            fields.append(QgsField(field_name_d90, QVariant.Double))

        sink: QgsFeatureSink
        sink, path_sink = self.parameterAsSink(parameters,
                                               self.OUTPUT,
                                               context,
                                               fields,
                                               layer_input.wkbType(),
                                               layer_input.sourceCrs())

        iterator = layer_input.getFeatures()

        for cnt, input_feature in enumerate(iterator):

            if feedback.isCanceled():
                break

            new_feature = QgsFeature(fields)
            new_feature.setGeometry(input_feature.geometry())

            # copy attributes
            attributes = input_feature.attributes()
            i = 0
            for att in attributes:
                new_feature.setAttribute(i, att)
                i += 1

            FTc = input_feature.attribute(att_ft)
            MTc = FTc + input_feature.attribute(att_mt)
            GTc = MTc + input_feature.attribute(att_gt)
            FUc = GTc + input_feature.attribute(att_fu)
            MUc = FUc + input_feature.attribute(att_mu)
            GUc = MUc + input_feature.attribute(att_gu)
            FSc = GUc + input_feature.attribute(att_fs)
            MSc = FSc + input_feature.attribute(att_ms)
            GSc = MSc + input_feature.attribute(att_gs)

            cumContents = {FTcode: FTc, MTcode: MTc, GTcode: GTc, FUcode: FUc, MUcode: MUc, GUcode: GUc, FScode: FSc,
                           MScode: MSc, GScode: GSc}

            cumCont = 0
            found = False

            for i in range(len(fractionCodes)):

                cumCont = cumCont + input_feature.attribute(fractionCodes[i])

                feedback.pushCommandInfo("{} : cummulative content: {} ; found is: {}".format(i,
                                                                                              cumCont,
                                                                                              found))

                if cumCont >= 90 and not found:
                    upSize = fractions[fractionCodes[i]][top]
                    botSize = fractions[fractionCodes[i]][bot]
                    upClassIndex = fractionCodes[i]
                    botClassIndex = fractionCodes[i - 1]
                    upClassContent = cumContents[upClassIndex]
                    botClassContent = cumContents[botClassIndex]

                    feedback.pushWarning("{}>{} - {}>{}".format(upClassIndex, upClassContent,
                                                                botClassIndex, botClassContent))
                    found = True

            d90 = botSize + (upSize - botSize) / (upClassContent - botClassContent) * (90 - botClassContent)

            if add_d90:
                new_feature.setAttribute(new_feature.fieldNameIndex(field_name_d90),
                                         d90)

            exp = 1.0 / 6.0
            n = (d90 ** exp) / 26.0

            new_feature.setAttribute(new_feature.fieldNameIndex(field_name_gb),
                                     n)

            sink.addFeature(new_feature)

            feedback.setProgress(int(cnt * total))

        return {self.OUTPUT: path_sink}
