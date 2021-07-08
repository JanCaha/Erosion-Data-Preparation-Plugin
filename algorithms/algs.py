from typing import Tuple, Dict, NoReturn, Union, List
import math

from PyQt5.QtCore import QVariant
from PyQt5 import QtWidgets

from qgis.core import (QgsVectorLayer,
                       QgsVectorDataProvider,
                       QgsFeature,
                       QgsFields,
                       QgsField)

from .utils import recode_2_ascii
from ..classes.catalog import E3dCatalog
from ..classes.class_KA5 import KA5Class
from ..classes.definition_landuse_crop import LanduseCrop
from ..constants import TextConstants
from ..algorithms.utils import log


def validate_KA5(layer_input: QgsVectorLayer,
                 field_name: str) -> Tuple[bool, str]:

    fields: QgsFields = layer_input.fields()

    attribute_index = fields.lookupField(field_name)

    unique_values = layer_input.uniqueValues(attribute_index)

    values_catalog = E3dCatalog().get_ka5_classes()

    missing_catalog_values = []

    for unique_value in unique_values:
        if unique_value not in values_catalog:
            missing_catalog_values.append(unique_value)

    return len(missing_catalog_values) == 0, ";".join(missing_catalog_values)


def classify_KA5(layer_input: QgsVectorLayer,
                 fieldname_FT: str,
                 fieldname_MT: str,
                 fieldname_GT: str,
                 fieldname_FU: str,
                 fieldname_MU: str,
                 fieldname_GU: str,
                 fieldname_FS: str,
                 fieldname_MS: str,
                 fieldname_GS: str,
                 fieldname_ka5_code: str,
                 fieldname_ka5_name: str,
                 fieldname_ka5_id: str,
                 progress_bar: QtWidgets.QProgressBar) -> [bool, str]:

    total = layer_input.dataProvider().featureCount() if layer_input.dataProvider().featureCount() else 0

    progress_bar.setMaximum(total)

    layer_input.startEditing()

    dp_input: QgsVectorDataProvider = layer_input.dataProvider()

    add_fields = QgsFields()
    add_fields.append(QgsField(fieldname_ka5_code, QVariant.String))
    add_fields.append(QgsField(fieldname_ka5_name, QVariant.String))
    add_fields.append(QgsField(fieldname_ka5_id, QVariant.String))
    add_fields.append(QgsField(TextConstants.field_name_ka5_group_lv2_id, QVariant.String))

    dp_input.addAttributes(add_fields)

    layer_input.updateFields()

    ka5_table = E3dCatalog().get_KA5_table()

    feature: QgsFeature

    for number, feature in enumerate(layer_input.getFeatures()):

        feature_data = KA5Class(None, None, None, None,
                                feature.attribute(fieldname_FT),
                                feature.attribute(fieldname_MT),
                                feature.attribute(fieldname_GT),
                                feature.attribute(fieldname_FU),
                                feature.attribute(fieldname_MU),
                                feature.attribute(fieldname_GU),
                                feature.attribute(fieldname_FS),
                                feature.attribute(fieldname_MS),
                                feature.attribute(fieldname_GS))

        min_rmse = math.inf
        min_rmse_code = None
        min_rmse_name = None
        min_rmse_id = None
        min_rmse_ka5_group_lv2 = None

        for ka5_cat in ka5_table:

            rmse = ka5_cat.RMSE(feature_data)

            if rmse < min_rmse:
                min_rmse = rmse
                min_rmse_code = ka5_cat.code
                min_rmse_name = ka5_cat.name
                min_rmse_id = ka5_cat.id
                min_rmse_ka5_group_lv2 = ka5_cat.group_lv2_id

        layer_input.changeAttributeValue(feature.id(),
                                         feature.fieldNameIndex(fieldname_ka5_name),
                                         min_rmse_name)

        layer_input.changeAttributeValue(feature.id(),
                                         feature.fieldNameIndex(fieldname_ka5_code),
                                         min_rmse_code)

        layer_input.changeAttributeValue(feature.id(),
                                         feature.fieldNameIndex(fieldname_ka5_id),
                                         min_rmse_id)

        layer_input.changeAttributeValue(feature.id(),
                                         feature.fieldNameIndex(TextConstants.field_name_ka5_group_lv2_id),
                                         min_rmse_ka5_group_lv2)

        progress_bar.setValue(int(number))

    layer_input.commitChanges()

    return True, ""


def calculate_garbrecht_roughness(layer_input: QgsVectorLayer,
                                  add_d90: bool,
                                  field_name_d90: str,
                                  field_name_gb: str,
                                  FTcode: str,
                                  MTcode: str,
                                  GTcode: str,
                                  FUcode: str,
                                  MUcode: str,
                                  GUcode: str,
                                  FScode: str,
                                  MScode: str,
                                  GScode: str,
                                  progress_bar: QtWidgets.QProgressBar) -> [bool, str]:

    # array of fraction codes - needed for iterating the fractions in right order
    fractionCodes = [FTcode, MTcode, GTcode, FUcode, MUcode, GUcode, FScode, MScode, GScode]

    fields: QgsFields = layer_input.fields()
    field: QgsField
    for frac_code in fractionCodes:
        if fields.lookupField(frac_code) == -1:
            return False, "Field `{}` could not be found in the layer, but it is required.".format(frac_code)

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

    total = layer_input.dataProvider().featureCount() if layer_input.dataProvider().featureCount() else 0

    progress_bar.setMaximum(total)

    layer_input.startEditing()

    feature_polygon: QgsFeature

    dp_input: QgsVectorDataProvider = layer_input.dataProvider()

    add_fields = QgsFields()
    add_fields.append(QgsField(field_name_gb, QVariant.Double))

    if add_d90:
        add_fields.append(QgsField(field_name_d90, QVariant.Double))

    dp_input.addAttributes(add_fields)

    layer_input.updateFields()

    feature: QgsFeature

    for number, feature in enumerate(layer_input.getFeatures()):

        FTc = feature.attribute(fractionCodes[0])
        MTc = FTc + feature.attribute(fractionCodes[1])
        GTc = MTc + feature.attribute(fractionCodes[2])
        FUc = GTc + feature.attribute(fractionCodes[3])
        MUc = FUc + feature.attribute(fractionCodes[4])
        GUc = MUc + feature.attribute(fractionCodes[5])
        FSc = GUc + feature.attribute(fractionCodes[6])
        MSc = FSc + feature.attribute(fractionCodes[7])
        GSc = MSc + feature.attribute(fractionCodes[8])

        cumContents = {FTcode: FTc, MTcode: MTc, GTcode: GTc, FUcode: FUc, MUcode: MUc, GUcode: GUc, FScode: FSc,
                       MScode: MSc, GScode: GSc}

        cumCont = 0
        found = False

        for i in range(len(fractionCodes)):

            cumCont = cumCont + feature.attribute(fractionCodes[i])

            if cumCont >= 90 and not found:
                upSize = fractions[fractionCodes[i]][top]
                botSize = fractions[fractionCodes[i]][bot]
                upClassIndex = fractionCodes[i]
                botClassIndex = fractionCodes[i - 1]
                upClassContent = cumContents[upClassIndex]
                botClassContent = cumContents[botClassIndex]

                found = True

        d90 = botSize + (upSize - botSize) / (upClassContent - botClassContent) * (90 - botClassContent)

        if add_d90:
            layer_input.changeAttributeValue(feature.id(),
                                             feature.fieldNameIndex(field_name_d90),
                                             d90)

        exp = 1.0 / 6.0
        n = (d90 ** exp) / 26.0

        layer_input.changeAttributeValue(feature.id(),
                                         feature.fieldNameIndex(field_name_gb),
                                         n)

        progress_bar.setValue(int(number))

    layer_input.commitChanges()

    return True, ""


def landuse_with_crops(layer_input: QgsVectorLayer,
                       fieldname_landuse: str,
                       fieldname_crop: str,
                       progress_bar: QtWidgets.QProgressBar) -> [bool, str]:

    fieldname_new = TextConstants.field_name_landuse_crops

    total = layer_input.dataProvider().featureCount() if layer_input.dataProvider().featureCount() else 0

    progress_bar.setMaximum(total)

    layer_input.startEditing()

    feature_polygon: QgsFeature

    dp_input: QgsVectorDataProvider = layer_input.dataProvider()

    fields: QgsFields = layer_input.fields()

    attribute_index = fields.lookupField(fieldname_new)

    if 0 < attribute_index:
        layer_input.deleteAttribute(attribute_index)
        layer_input.commitChanges(stopEditing=False)

    add_fields = QgsFields()

    field = QgsField(fieldname_new, QVariant.String, "", 255)

    add_fields.append(field)

    dp_input.addAttributes(add_fields)

    layer_input.updateFields()

    feature: QgsFeature

    for number, feature in enumerate(layer_input.getFeatures()):

        result = feature.attribute(fieldname_landuse)

        if fieldname_crop:
            if feature.attribute(fieldname_crop):
                result = "{}_{}".format(result, recode_2_ascii(feature.attribute(fieldname_crop)))

        layer_input.changeAttributeValue(feature.id(),
                                         feature.fieldNameIndex(fieldname_new),
                                         result)

        progress_bar.setValue(int(number))

    layer_input.commitChanges()

    return True, ""


def add_fields_to_landuse(layer: QgsVectorLayer,
                          dict_assigned_values: Dict[str, LanduseCrop]) -> NoReturn:

    layer_dp: QgsVectorDataProvider = layer.dataProvider()

    fields = [TextConstants.field_name_landuse_lv1_id,
              TextConstants.field_name_landuse_lv2_id,
              TextConstants.field_name_crop_id,
              TextConstants.field_name_crop_name]

    fields_to_delete = []

    for field in fields:

        index = layer_dp.fieldNameIndex(field)

        if 0 < index:
            fields_to_delete.append(index)

    layer.startEditing()
    layer.deleteAttributes(fields_to_delete)
    layer.commitChanges()

    add_fields = QgsFields()

    field = QgsField(TextConstants.field_name_landuse_lv1_id, QVariant.String, "", 255)
    add_fields.append(field)

    field = QgsField(TextConstants.field_name_landuse_lv2_id, QVariant.String, "", 255)
    add_fields.append(field)

    field = QgsField(TextConstants.field_name_crop_id, QVariant.String, "", 255)
    add_fields.append(field)

    field = QgsField(TextConstants.field_name_crop_name, QVariant.String, "", 255)
    add_fields.append(field)

    layer_dp.addAttributes(add_fields)

    layer.updateFields()

    layer.startEditing()

    feature: QgsFeature

    for feature in layer.getFeatures():

        landuse_crop = feature.attribute(TextConstants.field_name_landuse_crops)

        landuse_crop_element = dict_assigned_values[landuse_crop]

        if landuse_crop_element:

            layer.changeAttributeValue(feature.id(),
                                       feature.fieldNameIndex(TextConstants.field_name_landuse_lv1_id),
                                       landuse_crop_element.id_landuse_lv1)

            layer.changeAttributeValue(feature.id(),
                                       feature.fieldNameIndex(TextConstants.field_name_landuse_lv2_id),
                                       landuse_crop_element.id_landuse_lv2)

            layer.changeAttributeValue(feature.id(),
                                       feature.fieldNameIndex(TextConstants.field_name_crop_id),
                                       landuse_crop_element.id_crop)

            layer.changeAttributeValue(feature.id(),
                                       feature.fieldNameIndex(TextConstants.field_name_crop_name),
                                       landuse_crop_element.name)

    layer.commitChanges()


def delete_fields(layer: QgsVectorLayer,
                  fields: Union[str, List[str]]) -> NoReturn:

    if not isinstance(fields, List):
        fields = [fields]

    layer_dp: QgsVectorDataProvider = layer.dataProvider()

    fields_to_delete = []

    for field_name in fields:
        fields_to_delete.append(layer_dp.fieldNameIndex(field_name))

    layer.startEditing()
    layer.deleteAttributes(fields_to_delete)
    layer.commitChanges()
