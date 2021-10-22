from typing import Tuple, List, NoReturn, Optional, Any, Dict

from qgis.core import (QgsVectorLayer,
                       QgsRasterLayer,
                       QgsFields)
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import QVariant

from .constants import TextConstants
from .algorithms.algorithms_layers import (join_tables,
                                           intersect_dissolve,
                                           copy_layer_fix_geoms,
                                           create_table_KA5_to_join,
                                           rasterize_layer_by_example,
                                           retain_only_fields,
                                           replace_raster_values_by_raster,
                                           find_difference_and_assign_value)
from .algorithms.algs import (landuse_with_crops,
                              validate_KA5,
                              classify_KA5,
                              add_field_with_constant_value,
                              add_fid_field,
                              rename_field,
                              max_value_in_field,
                              add_row_without_geom,
                              delete_features_with_values,
                              delete_fields,
                              field_contains_null_values,
                              adjust_feature_values_to_settings)
from .algorithms.utils import add_maplayer_to_project


class E3DWizardProcess:

    # process parameters
    layer_soil: QgsVectorLayer = None
    layer_soil_input: QgsVectorLayer = None
    layer_landuse: QgsVectorLayer = None
    layer_landuse_fields_backup: QgsFields = None

    layer_soil_interstep: QgsVectorLayer = None
    layer_landuse_interstep: QgsVectorLayer = None

    layer_intersected_dissolved: QgsVectorLayer = None
    layer_raster_dtm: QgsRasterLayer = None
    layer_pour_points_rasterized: QgsRasterLayer = None
    layer_raster_rasterized: QgsRasterLayer = None
    date_month: int = None
    layer_export_parameters: QgsVectorLayer = None
    layer_export_lookup: QgsVectorLayer = None
    layer_export_e3d: QgsVectorLayer = None

    layer_channel_elements: QgsRasterLayer = None
    layer_drain_elements: QgsVectorLayer = None
    layer_pour_points: QgsVectorLayer = None

    poly_nr_additons: List[Tuple[int, str]] = []

    fields_to_remove_soil_layer = ["fid", "objectid", "shape_length", "shape_area"]

    dissolve_list = [TextConstants.field_name_ka5_id,
                     TextConstants.field_name_ka5_name,
                     TextConstants.field_name_ka5_code,
                     TextConstants.field_name_ka5_group_lv1_id,
                     TextConstants.field_name_ka5_group_lv2_id,
                     TextConstants.field_name_landuse_lv1_id,
                     TextConstants.field_name_landuse_lv2_id,
                     TextConstants.field_name_crop_id,
                     TextConstants.field_name_crop_name,
                     TextConstants.field_name_soil_id,
                     TextConstants.field_name_landuse_crops,
                     TextConstants.field_name_poly_id,
                     TextConstants.field_name_FU,
                     TextConstants.field_name_MU,
                     TextConstants.field_name_GU,
                     TextConstants.field_name_FT,
                     TextConstants.field_name_MT,
                     TextConstants.field_name_GT,
                     TextConstants.field_name_FS,
                     TextConstants.field_name_MS,
                     TextConstants.field_name_GS,
                     TextConstants.field_name_agrotechnology,
                     TextConstants.field_name_protection_measure,
                     TextConstants.field_name_vegetation_conditions,
                     TextConstants.field_name_surface_conditions,
                     TextConstants.field_name_init_moisture]

    DEFAULT_EXPORT_VALUES = {TextConstants.field_name_bulk_density: 1,
                             TextConstants.field_name_corg: 1,
                             TextConstants.field_name_roughness: 1,
                             TextConstants.field_name_canopy_cover: 1,
                             TextConstants.field_name_skinfactor: 1,
                             TextConstants.field_name_erodibility: 1,
                             TextConstants.field_name_FT: 0,
                             TextConstants.field_name_MT: 0,
                             TextConstants.field_name_GT: 0,
                             TextConstants.field_name_FU: 0,
                             TextConstants.field_name_MU: 0,
                             TextConstants.field_name_GU: 0,
                             TextConstants.field_name_FS: 0,
                             TextConstants.field_name_MS: 0,
                             TextConstants.field_name_GS: 0}

    def __init__(self):
        pass

    @property
    def layer_main(self):
        return self.layer_intersected_dissolved

    @layer_main.setter
    def layer_main(self, input_layer: QgsVectorLayer):
        self.layer_intersected_dissolved = input_layer

    def set_layer_soil(self, layer: QgsVectorLayer) -> NoReturn:

        self.layer_soil_input = copy_layer_fix_geoms(layer,
                                                     TextConstants.layer_soil)
        self.layer_soil = self.layer_soil_input

    def soil_2_soil_input(self):
        self.layer_soil_input = self.layer_soil

    def soil_input_2_soil(self):
        self.layer_soil = self.layer_soil_input.clone()

    def set_layer_landuse(self, layer: QgsVectorLayer) -> NoReturn:

        self.layer_landuse = copy_layer_fix_geoms(layer,
                                                  TextConstants.layer_landuse)

    def set_layer_raster_dtm(self, layer: QgsRasterLayer) -> NoReturn:
        self.layer_raster_dtm = layer

    def set_layer_channel_elements(self, layer: Optional[QgsRasterLayer]) -> NoReturn:

        if layer:
            self.layer_channel_elements = layer
        else:
            self.layer_channel_elements = None

    def set_layer_drain_elements(self, layer: Optional[QgsVectorLayer]) -> NoReturn:

        if layer:
            self.layer_drain_elements = copy_layer_fix_geoms(layer,
                                                             TextConstants.layer_drain_elements)
        else:
            self.layer_drain_elements = None

    def set_layer_pour_points(self, layer: Optional[QgsVectorLayer]) -> NoReturn:

        if layer:

            self.layer_pour_points = layer

        else:

            self.layer_pour_points = None
            self.layer_pour_points_rasterized = None

    def get_fields_pour_points_layer(self) -> QgsFields:
        return self.layer_pour_points.fields()

    def get_fields_soil_layer(self) -> QgsFields:

        fields = self.layer_soil.fields()

        for field_to_remove in self.fields_to_remove_soil_layer:
            index = fields.lookupField(field_to_remove)
            if index != -1:
                fields.remove(index)

        return fields

    def get_field_names_soil_layer(self) -> List[str]:

        field_names = [""]

        fields = self.get_fields_soil_layer()

        for field in fields:
            if field.name() not in self.fields_to_remove_soil_layer:
                if field.isNumeric() and not field_contains_null_values(self.layer_soil, field.name()):
                    field_names.append(field.name())

        return field_names

    def get_fields_landuse_layer(self) -> QgsFields:

        return self.layer_landuse.fields()

    def get_fields_for_layer(self, layer_name: str) -> QgsFields:
        return self.layer_based_on_keyword(layer_name).fields()

    def join_ka5_2_layer_soil(self,
                              ka5_field: str,
                              progress_bar: Optional[QProgressBar] = None):

        layer_ka5 = create_table_KA5_to_join()

        self.layer_soil = join_tables(self.layer_soil,
                                      ka5_field,
                                      layer_ka5,
                                      TextConstants.field_name_ka5_code,
                                      progress_bar=progress_bar)

    def classify_ka5(self, progress_bar: QProgressBar) -> NoReturn:
        classify_KA5(self.layer_soil,
                     TextConstants.field_name_FT,
                     TextConstants.field_name_MT,
                     TextConstants.field_name_GT,
                     TextConstants.field_name_FU,
                     TextConstants.field_name_MU,
                     TextConstants.field_name_GU,
                     TextConstants.field_name_FS,
                     TextConstants.field_name_MS,
                     TextConstants.field_name_GS,
                     TextConstants.field_name_ka5_code,
                     TextConstants.field_name_ka5_name,
                     TextConstants.field_name_ka5_id,
                     progress_bar)

    def merge_landuse_with_crops(self,
                                 field_name_landuse: str,
                                 field_name_crop: str,
                                 progress_bar: QProgressBar) -> NoReturn:
        landuse_with_crops(self.layer_landuse,
                           field_name_landuse,
                           field_name_crop,
                           progress_bar)

    def backup_fields_landuse(self):
        self.layer_landuse_fields_backup = self.layer_landuse.fields()

    def backup_input_layers(self):
        self.layer_soil_interstep = self.layer_soil
        self.layer_landuse_interstep = self.layer_landuse

    def restore_input_layers(self):
        self.layer_landuse = self.layer_landuse_interstep
        self.layer_soil = self.layer_soil_interstep

    def join_catalog_info_layer_landuse(self,
                                        table_to_join: QgsVectorLayer,
                                        progress_bar: QProgressBar) -> NoReturn:

        self.layer_landuse = retain_only_fields(self.layer_landuse,
                                                self.layer_landuse_fields_backup.names())

        self.layer_landuse = join_tables(self.layer_landuse,
                                         TextConstants.field_name_landuse_crops,
                                         table_to_join,
                                         TextConstants.field_name_landuse_crops,
                                         progress_bar)

    def adjust_search_values(self, table: Dict[str, str]):

        adjust_feature_values_to_settings(self.layer_intersected_dissolved,
                                          table)

    def rename_soil_field_soil_id(self, field_to_rename: str) -> NoReturn:

        rename_field(self.layer_soil,
                     field_to_rename,
                     TextConstants.field_name_soil_id)

    def handle_particle_size_field(self,
                                   field_name_constant: str,
                                   field_name_selected: str) -> NoReturn:

        if field_name_selected != field_name_constant:

            delete_fields(self.layer_soil, field_name_constant)

        if 0 < len(field_name_selected):

            rename_field(self.layer_soil, field_name_selected, field_name_constant)

        else:

            add_field_with_constant_value(self.layer_soil, field_name_constant, 0)

    def layer_based_on_keyword(self, layer_name: str) -> Optional[QgsVectorLayer]:

        if "Soil" in layer_name:
            return self.layer_soil

        elif "Landuse" in layer_name:
            return self.layer_landuse

        else:
            return None

    def rename_initmoisture(self,
                            layer_name: str,
                            field_name: str) -> NoReturn:

        if 0 < len(field_name):

            rename_field(self.layer_based_on_keyword(layer_name),
                         field_name,
                         TextConstants.field_name_init_moisture)

        else:

            add_field_with_constant_value(self.layer_soil,
                                          TextConstants.field_name_init_moisture,
                                          0.0,
                                          data_type=QVariant.Double)

    def rename_corg(self,
                    layer_name: str,
                    field_name: str) -> NoReturn:

        if 0 < len(field_name):

            rename_field(self.layer_based_on_keyword(layer_name),
                         field_name,
                         TextConstants.field_name_corg)

        self.dissolve_list = self.dissolve_list + [TextConstants.field_name_corg]

    def rename_bulkdensity(self,
                           layer_name: str,
                           field_name: str) -> NoReturn:

        if 0 < len(field_name):

            rename_field(self.layer_based_on_keyword(layer_name),
                         field_name,
                         TextConstants.field_name_bulk_density)

        self.dissolve_list = self.dissolve_list + [TextConstants.field_name_bulk_density]

    def rename_roughness(self,
                         layer_name: str,
                         field_name: str) -> NoReturn:

        if 0 < len(field_name):

            rename_field(self.layer_based_on_keyword(layer_name),
                         field_name,
                         TextConstants.field_name_roughness)

        self.dissolve_list = self.dissolve_list + [TextConstants.field_name_roughness]

    def rename_cover(self,
                         layer_name: str,
                         field_name: str) -> NoReturn:

        if 0 < len(field_name):
            rename_field(self.layer_based_on_keyword(layer_name),
                         field_name,
                         TextConstants.field_name_canopy_cover)

        self.dissolve_list = self.dissolve_list + [TextConstants.field_name_canopy_cover]

    def create_main_layer(self, progress_bar: QProgressBar) -> NoReturn:

        self.layer_intersected_dissolved = intersect_dissolve(self.layer_soil,
                                                              self.layer_landuse,
                                                              TextConstants.field_name_poly_id,
                                                              TextConstants.field_name_soil_id,
                                                              TextConstants.field_name_landuse_crops,
                                                              self.dissolve_list,
                                                              progress_bar)

    def add_month_field(self, value: int) -> NoReturn:

        add_field_with_constant_value(self.layer_intersected_dissolved,
                                      TextConstants.field_name_month,
                                      value,
                                      data_type=QVariant.Int)

    def remove_additions_fids_if_exist(self) -> Optional[List]:

        if not len(self.poly_nr_additons) == 0:

            fids_to_delete = []

            for fid_value, poly_id in self.poly_nr_additons:
                fids_to_delete.append(fid_value)

            delete_features_with_values(self.layer_intersected_dissolved,
                                        TextConstants.field_name_fid,
                                        fids_to_delete)

            return []

    def add_fid_field(self) -> NoReturn:
        add_fid_field(self.layer_intersected_dissolved)

    def rasterize_main_layer(self,
                             progress_bar: QProgressBar):

        self.layer_raster_rasterized = rasterize_layer_by_example(self.layer_intersected_dissolved,
                                                                  TextConstants.field_name_fid,
                                                                  self.layer_raster_dtm,
                                                                  progress_bar)

    @property
    def layer_main_raster(self) -> QgsRasterLayer:
        return self.layer_raster_rasterized

    def add_channel_elements(self) -> NoReturn:

        if self.layer_channel_elements:

            value = max_value_in_field(self.layer_intersected_dissolved,
                                       TextConstants.field_name_fid)

            value = int(value + 1)

            self.poly_nr_additons.append((value, "channel_elements"))

            raster = find_difference_and_assign_value(self.layer_raster_dtm,
                                                      self.layer_channel_elements,
                                                      value)

            self.layer_raster_rasterized = replace_raster_values_by_raster(self.layer_raster_rasterized,
                                                                           raster)

    def add_drain_elements(self) -> NoReturn:

        if self.layer_drain_elements:

            value = max_value_in_field(self.layer_intersected_dissolved,
                                       TextConstants.field_name_fid)

            value += 1

            if 0 < len(self.poly_nr_additons):
                value = self.poly_nr_additons[-1]
                value = int(value[0] + 1)

            self.poly_nr_additons.append((value, "drain_elements"))

            add_field_with_constant_value(self.layer_drain_elements,
                                          TextConstants.field_name_fid,
                                          value)

            raster = rasterize_layer_by_example(self.layer_drain_elements,
                                                TextConstants.field_name_fid,
                                                self.layer_raster_dtm)

            self.layer_raster_rasterized = replace_raster_values_by_raster(self.layer_raster_rasterized,
                                                                           raster)

    def add_poly_nr_rows(self) -> NoReturn:

        # add rows for channel elements and drain elements
        for fid_value, poly_id in self.poly_nr_additons:
            values = {TextConstants.field_name_fid: fid_value,
                      TextConstants.field_name_init_moisture: 0.0,
                      TextConstants.field_name_poly_id: poly_id}

            values.update(self.DEFAULT_EXPORT_VALUES)

            add_row_without_geom(self.layer_intersected_dissolved, values)

    def add_fields_contant(self):

        add_field_with_constant_value(self.layer_intersected_dissolved,
                                      TextConstants.field_name_layer_id,
                                      0)

        add_field_with_constant_value(self.layer_intersected_dissolved,
                                      TextConstants.field_name_layer_thick,
                                      10000)

    @property
    def layer_parameters(self) -> QgsVectorLayer:

        return self.layer_export_parameters

    def prepare_layer_parameters(self) -> NoReturn:

        self.layer_export_parameters = retain_only_fields(self.layer_intersected_dissolved,
                                                          [TextConstants.field_name_poly_id,
                                                           TextConstants.field_name_layer_id,
                                                           TextConstants.field_name_layer_thick,
                                                           TextConstants.field_name_FT,
                                                           TextConstants.field_name_MT,
                                                           TextConstants.field_name_GT,
                                                           TextConstants.field_name_FU,
                                                           TextConstants.field_name_MU,
                                                           TextConstants.field_name_GU,
                                                           TextConstants.field_name_FS,
                                                           TextConstants.field_name_GS,
                                                           TextConstants.field_name_MS,
                                                           TextConstants.field_name_bulk_density,
                                                           TextConstants.field_name_corg,
                                                           TextConstants.field_name_init_moisture,
                                                           TextConstants.field_name_roughness,
                                                           TextConstants.field_name_canopy_cover,
                                                           TextConstants.field_name_skinfactor,
                                                           TextConstants.field_name_erodibility],
                                                          "parameters")

    @property
    def layer_lookup(self) -> QgsVectorLayer:
        return self.layer_export_lookup

    def prepare_layer_lookup(self) -> NoReturn:

        self.layer_export_lookup = retain_only_fields(self.layer_intersected_dissolved,
                                                      [TextConstants.field_name_poly_id,
                                                       TextConstants.field_name_fid],
                                                      "lookup")

    @property
    def layer_e3d(self) -> QgsVectorLayer:
        return self.layer_export_e3d

    def prepare_layer_e3d(self) -> NoReturn:

        self.layer_export_e3d = retain_only_fields(self.layer_intersected_dissolved,
                                                   [TextConstants.field_name_fid,
                                                    TextConstants.field_name_poly_id,
                                                    TextConstants.field_name_layer_id,
                                                    TextConstants.field_name_layer_thick,
                                                    TextConstants.field_name_FT,
                                                    TextConstants.field_name_MT,
                                                    TextConstants.field_name_GT,
                                                    TextConstants.field_name_FU,
                                                    TextConstants.field_name_MU,
                                                    TextConstants.field_name_GU,
                                                    TextConstants.field_name_FS,
                                                    TextConstants.field_name_GS,
                                                    TextConstants.field_name_MS,
                                                    TextConstants.field_name_bulk_density,
                                                    TextConstants.field_name_corg,
                                                    TextConstants.field_name_init_moisture,
                                                    TextConstants.field_name_roughness,
                                                    TextConstants.field_name_canopy_cover,
                                                    TextConstants.field_name_skinfactor,
                                                    TextConstants.field_name_erodibility],
                                                   "E3D export layer")

    def prepare_pour_points(self,
                            field_name: str) -> NoReturn:

        if self.layer_pour_points:

            self.layer_pour_points_rasterized = rasterize_layer_by_example(self.layer_pour_points,
                                                                           field_name,
                                                                           self.layer_raster_dtm)