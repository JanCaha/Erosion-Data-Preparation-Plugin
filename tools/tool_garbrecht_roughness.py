from PyQt5.QtCore import QVariant

from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterVectorLayer,
                       QgsFeature,
                       QgsVectorDataProvider,
                       QgsFields,
                       QgsField,
                       QgsProcessingFeedback,
                       QgsVectorLayer)

from ..constants import TextConstants

# TODO add input parameters


class GarbrechtRougnessProcessingAlgorithm(QgsProcessingAlgorithm):

    INPUT = "Input"
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
        return "GarbrechtRougness"

    def displayName(self):
        return "Calculate Garbrecht roughness from structural subclasses content"

    def group(self):
        return "Erosion-3D Data Plugin"

    def groupId(self):
        return 'erosiondataplugin'

    def shortHelpString(self):
        return "Calculate Garbrech roughness based on D90 diameter"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                "Input feature layer:")
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.D90,
                "Add D90 field into the input table and write the values?"
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.D90NAME,
                "Set D90 field name:",
                "d90"
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.NNAME,
                "Set Garbrech roughness field name:",
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

        dp_input: QgsVectorDataProvider = layer_input.dataProvider()

        add_fields = QgsFields()
        add_fields.append(QgsField(field_name_gb, QVariant.Double))

        if add_d90:
            add_fields.append(QgsField(field_name_d90, QVariant.Double))

        dp_input.addAttributes(add_fields)

        layer_input.updateFields()

        fields = fractionCodes + [field_name_gb]

        if add_d90:
            fields += [field_name_d90]

        feature: QgsFeature

        for number, feature in enumerate(layer_input.getFeatures()):

            FTc = feature.attribute(att_ft)
            MTc = FTc + feature.attribute(att_mt)
            GTc = MTc + feature.attribute(att_gt)
            FUc = GTc + feature.attribute(att_fu)
            MUc = FUc + feature.attribute(att_mu)
            GUc = MUc + feature.attribute(att_gu)
            FSc = GUc + feature.attribute(att_fs)
            MSc = FSc + feature.attribute(att_ms)
            GSc = MSc + feature.attribute(att_gs)

            cumContents = {FTcode: FTc, MTcode: MTc, GTcode: GTc, FUcode: FUc, MUcode: MUc, GUcode: GUc, FScode: FSc,
                           MScode: MSc, GScode: GSc}

            cumCont = 0
            found = False

            for i in range(len(fractionCodes)):

                cumCont = cumCont + feature.attribute(fractionCodes[i])

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
                layer_input.changeAttributeValue(feature.id(),
                                                 feature.fieldNameIndex(field_name_d90),
                                                 d90)

            feedback.pushCommandInfo(str(d90) + " - " + str(type(d90)))

            exp = 1.0 / 6.0
            n = (d90 ** exp) / 26.0

            layer_input.changeAttributeValue(feature.id(),
                                             feature.fieldNameIndex(field_name_gb),
                                             n)

            feedback.setProgress(int(number * total))

        layer_input.commitChanges()

        return {}
