from typing import List, Dict, Union, Optional

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QVariant

from qgis import processing

from qgis.core import (QgsVectorDataProvider,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsMapLayer,
                       QgsVectorLayer,
                       QgsRasterDataProvider,
                       QgsRectangle,
                       QgsCoordinateReferenceSystem,
                       QgsRasterLayer,
                       QgsRasterBandStats,
                       QgsProcessingUtils,
                       QgsCoordinateTransformContext)

from processing.algs.gdal.GdalUtils import GdalUtils

from qgis.analysis import (QgsRasterCalculatorEntry, QgsRasterCalculator)

from ..classes.definition_landuse_crop import LanduseCrop
from ..classes.definition_landuse_values import LanduseValues
from ..constants import TextConstants
from ..classes.catalog import E3dCatalog
from ..classes.class_KA5 import KA5Class
from ..algorithms.utils import log, add_maplayer_to_project


def rasterize_layer_by_example(vector_layer: QgsVectorLayer,
                               field_name_vectorize: str,
                               raster_template: QgsRasterLayer,
                               progress_bar: Optional[QtWidgets.QProgressBar] = None) -> QgsRasterLayer:

    if not progress_bar:
        progress_bar = QtWidgets.QProgressBar()

    progress_bar.setMaximum(3)
    progress_bar.setValue(1)

    extent: QgsRectangle = raster_template.extent()

    crs: QgsCoordinateReferenceSystem = vector_layer.crs()

    extent_string = f"{extent.xMinimum()},{extent.xMaximum()},{extent.yMinimum()},{extent.yMaximum()} [{crs.authid()}]"

    raster_data_provider: QgsRasterDataProvider = raster_template.dataProvider()
    no_data = raster_data_provider.sourceNoDataValue(1)

    progress_bar.setValue(2)

    result = processing.run("gdal:rasterize",
                            {'INPUT': vector_layer,
                             'FIELD': field_name_vectorize,
                             'BURN': 0,
                             'UNITS': 0,
                             'WIDTH': raster_template.width(),
                             'HEIGHT': raster_template.height(),
                             'EXTENT': extent_string,
                             'NODATA': no_data,
                             'OPTIONS': '',
                             'DATA_TYPE': 5,
                             'INIT': None,
                             'INVERT': False,
                             'EXTRA': '',
                             'OUTPUT': 'TEMPORARY_OUTPUT'})

    progress_bar.setValue(3)

    return QgsRasterLayer(result["OUTPUT"], f"rasterized_{vector_layer.name()}")


def copy_layer_fix_geoms(layer_input: QgsMapLayer, layer_name: str) -> QgsVectorLayer:

    result = processing.run("native:fixgeometries",
                            {'INPUT': layer_input,
                             'OUTPUT': f"memory:{layer_name}"})

    return result["OUTPUT"]


def join_tables(layer_data: QgsVectorLayer,
                layer_data_field_name_join: Union[str, List[str]],
                layer_table: QgsVectorLayer,
                layer_table_field_name_join: Union[str, List[str]],
                progress_bar: QtWidgets.QProgressBar = None) -> QgsVectorLayer:

    if not progress_bar:
        progress_bar = QtWidgets.QProgressBar()

    merge_field_1 = "temp_merge_field_1"
    merge_field_2 = "temp_merge_field_2"

    progress_bar.setMaximum(4)

    if isinstance(layer_data_field_name_join, list):

        layer_data_dp: QgsVectorDataProvider = layer_data.dataProvider()

        add_fields = QgsFields()

        field = QgsField(merge_field_1, QVariant.String, "", 255)

        add_fields.append(field)

        layer_data_dp.addAttributes(add_fields)

        layer_data.updateFields()

        layer_data.startEditing()

        feature: QgsFeature

        for feature in layer_data.getFeatures():

            attributes = []

            for field_name in layer_data_field_name_join:

                value = feature.attribute(field_name)

                if not value:
                    value = ""

                attributes.append(str(value))

            if not all(x == "" for x in attributes):
                attributes = "_".join(attributes)

                layer_data.changeAttributeValue(feature.id(),
                                                feature.fieldNameIndex(merge_field_1),
                                                attributes)

        layer_data.commitChanges()

        layer_data_field_name_join = merge_field_1

    progress_bar.setValue(1)

    if isinstance(layer_table_field_name_join, list):

        layer_table_dp: QgsVectorDataProvider = layer_table.dataProvider()

        add_fields = QgsFields()

        field = QgsField(merge_field_2, QVariant.String, "", 255)

        add_fields.append(field)

        layer_table_dp.addAttributes(add_fields)

        layer_table.updateFields()

        layer_table.startEditing()

        feature: QgsFeature

        for feature in layer_table.getFeatures():

            attributes = []

            for field_name in layer_table_field_name_join:

                value = feature.attribute(field_name)

                if not value:
                    value = ""

                attributes.append(str(value))

            if not all(x == "" for x in attributes):
                attributes = "_".join(attributes)

                layer_table.changeAttributeValue(feature.id(),
                                                 feature.fieldNameIndex(merge_field_2),
                                                 attributes)
        layer_table.commitChanges()

        fields_to_delete = []
        for field_name in layer_table_field_name_join:
            fields_to_delete.append(layer_table_dp.fieldNameIndex(field_name))

        layer_table.startEditing()
        layer_table.deleteAttributes(fields_to_delete)
        layer_table.commitChanges()

        layer_table_field_name_join = merge_field_2

    progress_bar.setValue(2)

    result = processing.run('qgis:joinattributestable',
                            {'INPUT': layer_data,
                             'FIELD': layer_data_field_name_join,
                             'INPUT_2': layer_table,
                             'FIELD_2': layer_table_field_name_join,
                             'OUTPUT': f"memory:{layer_data.name()}"})

    progress_bar.setValue(3)

    if layer_data_field_name_join == merge_field_1 and layer_table_field_name_join == merge_field_2:

        result = processing.run("native:deletecolumn",
                                {'INPUT': result['OUTPUT'],
                                 'COLUMN': [layer_data_field_name_join, layer_table_field_name_join],
                                 'OUTPUT': f"memory:{layer_data.name()}"},)

    progress_bar.setValue(4)

    return result['OUTPUT']


def intersect_dissolve(layer_input_1: QgsVectorLayer,
                       layer_input_2: QgsVectorLayer,
                       fieldname_new: str,
                       fieldname_sid: str,
                       fieldname_landuse_crop: str,
                       dissolve_fields: List[str],
                       progress_bar: QtWidgets.QProgressBar) -> QgsVectorLayer:

    progress_bar.setMaximum(4)

    result = processing.run("native:intersection", {'INPUT': layer_input_1,
                                                    'OVERLAY': layer_input_2,
                                                    'INPUT_FIELDS': [],
                                                    'OVERLAY_FIELDS': [],
                                                    'OVERLAY_FIELDS_PREFIX': '',
                                                    'OUTPUT': 'memory:intersection'})

    layer_intersection: QgsVectorLayer = result["OUTPUT"]

    progress_bar.setValue(1)

    dp_layer_intersection: QgsVectorDataProvider = layer_intersection.dataProvider()

    add_fields = QgsFields()

    field = QgsField(fieldname_new, QVariant.String, "", 255)

    add_fields.append(field)

    dp_layer_intersection.addAttributes(add_fields)

    layer_intersection.updateFields()

    layer_intersection.startEditing()

    for number, feature in enumerate(layer_intersection.getFeatures()):

        attr_result = "{}_{}".format(feature.attribute(fieldname_landuse_crop),
                                     feature.attribute(fieldname_sid))

        layer_intersection.changeAttributeValue(feature.id(),
                                                feature.fieldNameIndex(fieldname_new),
                                                attr_result)

    layer_intersection.commitChanges()

    progress_bar.setValue(2)

    result = processing.run("native:retainfields", {'INPUT': layer_intersection,
                                                    'FIELDS': dissolve_fields,
                                                    'OUTPUT': 'memory:removed_fields'})

    progress_bar.setValue(3)

    result = processing.run("native:dissolve", {'INPUT': result["OUTPUT"],
                                                'FIELD': dissolve_fields,
                                                'OUTPUT': 'memory:dissolve'})

    progress_bar.setValue(4)

    return result["OUTPUT"]


def create_table_to_join(dict_assigned_values: Dict[str, LanduseValues],
                         dict_catalog_values: Dict[str, LanduseCrop]) -> QgsVectorLayer:

    fields = [F"field={TextConstants.vl_join_col_name}:string",
              F"field={TextConstants.tw_lv_col_bulkdensity}:double",
              F"field={TextConstants.tw_lv_col_initmoisture}:double",
              F"field={TextConstants.tw_lv_col_erodibility}:double",
              F"field={TextConstants.tw_lv_col_roughn}:double",
              F"field={TextConstants.tw_lv_col_cover}:double",
              F"field={TextConstants.tw_lv_col_skinfactor}:double"]

    fields = "&".join(fields)

    layer = QgsVectorLayer(
        F"NoGeometry?{fields}",
        "source",
        "memory")

    layer_dp: QgsVectorDataProvider = layer.dataProvider()

    for landuse_values in list(dict_assigned_values.values()):

        f = QgsFeature()

        f.setAttributes(landuse_values.get_fields_for_layer())

        layer_dp.addFeature(f)

    for (landuse_name, landuse_values) in dict_catalog_values.items():

        f = QgsFeature()

        f.setAttributes([landuse_name] + landuse_values.get_fields_for_layer())

        layer_dp.addFeature(f)

    return layer


def create_table_KA5_to_join() -> QgsVectorLayer:

    classes = E3dCatalog().get_KA5_table()

    fields = [F"field={TextConstants.field_name_ka5_code}:string",
              F"field={TextConstants.field_name_ka5_group_lv2_id}:string",
              F"field=ka5_ft:double",
              F"field=ka5_mt:double",
              F"field=ka5_gt:double",
              F"field=ka5_fu:double",
              F"field=ka5_mu:double",
              F"field=ka5_gu:double",
              F"field=ka5_fs:double",
              F"field=ka5_ms:double",
              F"field=ka5_gs:double"]

    fields = "&".join(fields)

    layer = QgsVectorLayer(
        F"NoGeometry?{fields}",
        "ka5_data",
        "memory")

    layer_dp: QgsVectorDataProvider = layer.dataProvider()

    ka5_class: KA5Class

    for ka5_class in classes:

        f = QgsFeature()

        f.setAttributes([ka5_class.code, ka5_class.group_lv2_id,
                         ka5_class.FT, ka5_class.MT, ka5_class.GT,
                         ka5_class.FU, ka5_class.MU, ka5_class.GU,
                         ka5_class.FS, ka5_class.MS, ka5_class.GS])

        layer_dp.addFeature(f)

    return layer


def retain_only_fields(layer: QgsVectorLayer,
                       fields_to_retain: List[str],
                       result_layer_name: Optional[str] = None) -> QgsVectorLayer:

    if result_layer_name:
        layer_name = f"memory:{result_layer_name}"
    else:
        layer_name = f"memory:{layer.name()}"

    result = processing.run("native:retainfields",
                            {'INPUT': layer,
                             'FIELDS': fields_to_retain,
                             'OUTPUT': layer_name})

    return result["OUTPUT"]


def replace_raster_values_by_raster(raster_orig: QgsRasterLayer,
                                    raster_new_values: QgsRasterLayer,
                                    progress_bar: QtWidgets.QProgressBar) -> QgsRasterLayer:

    progress_bar.setMaximum(5)

    progress_bar.setValue(1)

    result = processing.run("native:fillnodata",
                            {'INPUT': raster_new_values,
                             'BAND': 1,
                             'FILL_VALUE': 0,
                             'OUTPUT': 'TEMPORARY_OUTPUT'})

    raster_new_values = QgsRasterLayer(result["OUTPUT"])

    progress_bar.setValue(2)

    raster_new_values_dp = raster_new_values.dataProvider()

    stats = raster_new_values_dp.bandStatistics(1, QgsRasterBandStats.All, raster_new_values.extent())
    max_value = str(round(stats.maximumValue))

    progress_bar.setValue(3)

    one_value_raster = QgsRasterCalculatorEntry()
    one_value_raster.ref = 'one_value_raster@1'
    one_value_raster.raster = raster_new_values
    one_value_raster.bandNumber = 1

    org_raster = QgsRasterCalculatorEntry()
    org_raster.ref = 'org_rast@1'
    org_raster.raster = raster_orig
    org_raster.bandNumber = 1

    raster_entries = []
    raster_entries.append(one_value_raster)
    raster_entries.append(org_raster)

    expression = "({0} != {1}) * {2} + {0}".format(one_value_raster.ref,
                                                   max_value,
                                                   org_raster.ref)

    extent = raster_orig.extent()
    output_raster_filename = QgsProcessingUtils.generateTempFilename("raster.tif")

    calc = QgsRasterCalculator(
        expression,
        output_raster_filename,
        GdalUtils.getFormatShortNameFromFilename(output_raster_filename),
        extent,
        raster_orig.crs(),
        int(extent.width()),
        int(extent.height()),
        raster_entries,
        QgsCoordinateTransformContext()
    )

    progress_bar.setValue(4)

    calc.processCalculation()

    progress_bar.setValue(5)

    return QgsRasterLayer(output_raster_filename)
