from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path
import sqlite3


from .singleton import Singleton
from .class_KA5 import KA5Class
from ..constants import TextConstants
from ..algorithms.utils import log


class E3dCatalog(metaclass=Singleton):

    default_stat_tuple = (None, None, None, 0)

    def __init__(self,
                 database_file: Optional[str] = None):

        self._data_quality_values = {}
        self._data_sources_values = {}

        if not database_file or not Path(database_file).exists():
            database_file = "database.sqlite"
            self.database_file = Path(__file__).parent.parent / "db_catalog" / database_file

        else:
            self.database_file = Path(database_file)

        self.db_connection = sqlite3.connect(self.database_file)

        self.db_cursor = self.db_connection.cursor()

    def set_data_quality(self, data: Dict) -> Dict:

        result = {}

        for key in data.keys():

            result.update({self.data_quality[key]: data[key]})

        return result

    @property
    def data_quality(self):

        if not self._data_quality_values:

            sql = f"SELECT id, name_{TextConstants.language} FROM quality_index"

            self.db_cursor.execute(sql)

            data = self.db_cursor.fetchall()

            for row in data:
                self._data_quality_values.update({row[0]: row[1]})

        return self._data_quality_values

    def set_data_sources(self, data: Dict) -> Dict:

        result = {}

        for key in data.keys():

            result.update({self.data_sources[key]: data[key]})

        return result

    @property
    def data_sources(self):

        if not self._data_sources_values:

            sql = f"SELECT id, name_{TextConstants.language} FROM source"

            self.db_cursor.execute(sql)

            data = self.db_cursor.fetchall()

            for row in data:
                self._data_sources_values.update({row[0]: row[1]})

        return self._data_sources_values

    def get_values(self, table: str, landuse_lv1_id: str, landuse_lv2_id: str, crop_id: str):

        wheres = []

        if landuse_lv1_id:
            wheres.append(f"landuse_lv1_id = {landuse_lv1_id}")
        else:
            wheres.append(f"landuse_lv1_id IS NULL")

        if landuse_lv2_id:
            wheres.append(f"landuse_lv2_id = {landuse_lv2_id}")
        else:
            wheres.append(f"landuse_lv2_id IS NULL")

        if crop_id:
            wheres.append(f"crop_id = {crop_id}")
        else:
            wheres.append(f"crop_id IS NULL")

        where = F"WHERE {' AND '.join(wheres)}"

        # TODO FIX query - corg and run_id are placeholders
        sql = f"SELECT bulkdensity, initmoisture, erodibility, corg, run_id, skinfactor FROM {table} {where}"

        self.db_cursor.execute(sql)

        return self.db_cursor.fetchone()

    def get_ka5_classes(self) -> List[str]:

        ka5_classes = []

        self.db_cursor.execute("SELECT code FROM ka5_class")

        rows = self.db_cursor.fetchall()

        for row in rows:
            ka5_classes.append(row[0])

        return ka5_classes

    def get_surface_condition(self) -> Dict[str, int]:

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id FROM surface_condition")

        rows = self.db_cursor.fetchall()

        data = {}

        for row in rows:

            data.update({row[0]: row[1]})

        return data

    def get_protection_measure(self) -> Dict[str, int]:

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id FROM protection_measure")

        rows = self.db_cursor.fetchall()

        data = {}

        for row in rows:

            data.update({row[0]: row[1]})

        return data

    def get_vegetation_condition(self) -> Dict[str, int]:

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id FROM vegetation_condition")

        rows = self.db_cursor.fetchall()

        data = {}

        for row in rows:

            data.update({row[0]: row[1]})

        return data

    def get_agrotechnology(self) -> Dict[str, int]:

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id FROM agrotechnology")

        rows = self.db_cursor.fetchall()

        data = {}

        for row in rows:

            data.update({row[0]: row[1]})

        return data

    def get_landuse_crop(self):  # -> Dict[str, LanduseCrop]:

        from .definition_landuse_crop import LanduseCrop

        # count = 0

        data = {}

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id FROM landuse_lv1")

        rows = self.db_cursor.fetchall()

        # count += len(rows)

        for row in rows:
            data.update({row[0]: LanduseCrop(object_id=row[1],
                                             name=row[0],
                                             table="landuse_lv1",
                                             id_landuse_lv1=row[1],
                                             id_landuse_lv2=None,
                                             id_crop=None)})

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id, landuse_lv1_id FROM landuse_lv2 "
                               f"ORDER BY name_{TextConstants.language}")

        rows = self.db_cursor.fetchall()

        # count += len(rows)

        for row in rows:
            data.update({row[0]: LanduseCrop(object_id=row[1],
                                             name=row[0],
                                             table="landuse_lv2",
                                             id_landuse_lv1=row[2],
                                             id_landuse_lv2=row[1],
                                             id_crop=None)})

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id, landuse_lv2_id FROM crop "
                               f"ORDER BY name_{TextConstants.language}")

        rows = self.db_cursor.fetchall()

        # count += len(rows)

        for row in rows:
            data.update({row[0]: LanduseCrop(object_id=row[1],
                                             name=row[0],
                                             table="crop",
                                             id_landuse_lv1=str(row[2])[0],
                                             id_landuse_lv2=row[2],
                                             id_crop=row[1])})

        # if count != len(list(data.keys())):
        #     raise RuntimeError("Problem with construction of landuse crop data!")

        return data

    def get_KA5_table(self) -> List[KA5Class]:

        classes = []

        self.db_cursor.execute(f"SELECT id, code, name_{TextConstants.language}, ka5_group_lv1_id, ka5_group_lv2_id,"
                               f"ft, mt, gt, fu, mu, gu, fs, ms, gs FROM ka5_class")

        rows = self.db_cursor.fetchall()

        for row in rows:
            classes.append(KA5Class.from_array(row))

        return classes

    def extract_values_sources_quality(self, data: List[Tuple]) -> Tuple[List[float], Dict[str, int], Dict[str, int]]:

        values = []
        source_id = {}
        quality_index = {}

        for row in data:

            values.append(row[0])

            if row[1] not in source_id.keys():
                source_id.update({row[1]: 1})
            else:
                number = source_id[row[1]]
                source_id.update({row[1]: number + 1})

            if row[2] not in quality_index.keys():
                quality_index.update({row[2]: 1})
            else:
                number = quality_index[row[2]]
                quality_index.update({row[2]: number + 1})

        source_id = self.set_data_sources(source_id)
        quality_index = self.set_data_quality(quality_index)

        return values, source_id, quality_index

    def prepare_bulk_density_conditions(self,
                                        ka5_class: Optional[str] = None,
                                        ka5_group_lv1: Optional[str] = None,
                                        ka5_group_lv2: Optional[str] = None,
                                        crop: Optional[str] = None,
                                        landuse_lv1: Optional[str] = None,
                                        landuse_lv2: Optional[str] = None,
                                        agrotechnology: Optional[str] = None,
                                        month: Optional[str] = None) -> List[str]:

        conds = []

        if ka5_group_lv1:
            conds.append(f"ka5_group_lv1_id = {ka5_group_lv1}")

        if ka5_group_lv2:
            conds.append(f"ka5_group_lv2_id = {ka5_group_lv2}")

        if agrotechnology:
            conds.append(f"agrotechnology_id = {agrotechnology}")

        if ka5_class:
            conds.append(f"ka5_class_id = {ka5_class}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

        if month:
            conds.append(f"month_id = {month}")

        return conds

    def get_bulk_density_data(self,
                              ka5_class: Optional[str] = None,
                              ka5_group_lv1: Optional[str] = None,
                              ka5_group_lv2: Optional[str] = None,
                              crop: Optional[str] = None,
                              landuse_lv1: Optional[str] = None,
                              landuse_lv2: Optional[str] = None,
                              agrotechnology: Optional[str] = None,
                              month: Optional[str] = None) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:

        conds = self.prepare_bulk_density_conditions(ka5_class,
                                                     ka5_group_lv1,
                                                     ka5_group_lv2,
                                                     crop,
                                                     landuse_lv1,
                                                     landuse_lv2,
                                                     agrotechnology,
                                                     month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT bulk_density, source_id, quality_index_id "
                                   F" FROM bulk_density "
                                   F"WHERE {conds}")

            data = self.db_cursor.fetchall()

            return self.extract_values_sources_quality(data)

        return None

    def get_bulk_density_range(self,
                               ka5_class: Optional[str] = None,
                               ka5_group_lv1: Optional[str] = None,
                               ka5_group_lv2: Optional[str] = None,
                               crop: Optional[str] = None,
                               landuse_lv1: Optional[str] = None,
                               landuse_lv2: Optional[str] = None,
                               agrotechnology: Optional[str] = None,
                               month: Optional[str] = None):

        conds = self.prepare_bulk_density_conditions(ka5_class,
                                                     ka5_group_lv1,
                                                     ka5_group_lv2,
                                                     crop,
                                                     landuse_lv1,
                                                     landuse_lv2,
                                                     agrotechnology,
                                                     month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT MIN(bulk_density) AS min, MAX(bulk_density) AS max, "
                                   F"AVG(bulk_density) AS mean, COUNT() AS count FROM bulk_density "
                                   F"WHERE {conds}")

            return self.check_stat_row(self.db_cursor.fetchall())

        else:
            return self.default_stat_tuple

    def get_corg_conditions(self,
                            ka5_class: Optional[str] = None,
                            ka5_group_lv1: Optional[str] = None,
                            ka5_group_lv2: Optional[str] = None,
                            crop: Optional[str] = None,
                            landuse_lv1: Optional[str] = None,
                            landuse_lv2: Optional[str] = None,
                            agrotechnology: Optional[str] = None) -> List[str]:

        conds = []

        if ka5_group_lv1:
            conds.append(f"ka5_group_lv1_id = {ka5_group_lv1}")

        if ka5_group_lv2:
            conds.append(f"ka5_group_lv2_id = {ka5_group_lv2}")

        if agrotechnology:
            conds.append(f"agrotechnology_id = {agrotechnology}")

        if ka5_class:
            conds.append(f"ka5_class_id = {ka5_class}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

        return conds

    def get_corg_range(self,
                       ka5_class: Optional[str] = None,
                       ka5_group_lv1: Optional[str] = None,
                       ka5_group_lv2: Optional[str] = None,
                       crop: Optional[str] = None,
                       landuse_lv1: Optional[str] = None,
                       landuse_lv2: Optional[str] = None,
                       agrotechnology: Optional[str] = None):

        conds = self.get_corg_conditions(ka5_class,
                                         ka5_group_lv1,
                                         ka5_group_lv2,
                                         crop,
                                         landuse_lv1,
                                         landuse_lv2,
                                         agrotechnology)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT MIN(corg) AS min, MAX(corg) AS max, AVG(corg) as mean, COUNT() as count FROM corg "
                                   F"WHERE {conds}")

            return self.check_stat_row(self.db_cursor.fetchall())

        else:
            return self.default_stat_tuple

    def get_corg_data(self,
                      ka5_class: Optional[str] = None,
                      ka5_group_lv1: Optional[str] = None,
                      ka5_group_lv2: Optional[str] = None,
                      crop: Optional[str] = None,
                      landuse_lv1: Optional[str] = None,
                      landuse_lv2: Optional[str] = None,
                      agrotechnology: Optional[str] = None) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:

        conds = self.get_corg_conditions(ka5_class,
                                         ka5_group_lv1,
                                         ka5_group_lv2,
                                         crop,
                                         landuse_lv1,
                                         landuse_lv2,
                                         agrotechnology)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT corg, source_id, quality_index_id "
                                   F" FROM corg "
                                   F"WHERE {conds}")

            data = self.db_cursor.fetchall()

            return self.extract_values_sources_quality(data)

        return None

    def get_canopy_cover_conditions(self,
                                    crop: Optional[str] = None,
                                    landuse_lv1: Optional[str] = None,
                                    landuse_lv2: Optional[str] = None,
                                    month: Optional[str] = None) -> List[str]:

        conds = []

        if month:
            conds.append(f"month_id = {month}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

        return conds

    def get_canopy_cover_range(self,
                               crop: Optional[str] = None,
                               landuse_lv1: Optional[str] = None,
                               landuse_lv2: Optional[str] = None,
                               month: Optional[str] = None):

        conds = self.get_canopy_cover_conditions(crop,
                                                 landuse_lv1,
                                                 landuse_lv2,
                                                 month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            variable_name = "canopy_cover"

            self.db_cursor.execute(
                F"SELECT "
                F"MIN({variable_name}) AS min, "
                F"MAX({variable_name}) AS max, "
                F"AVG({variable_name}) as mean, "
                F"COUNT() as count FROM canopy_cover "
                F"WHERE {conds}")

            return self.check_stat_row(self.db_cursor.fetchall())

        else:
            return self.default_stat_tuple

    def get_canopy_cover_data(self,
                              crop: Optional[str] = None,
                              landuse_lv1: Optional[str] = None,
                              landuse_lv2: Optional[str] = None,
                              month: Optional[str] = None) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:

        conds = self.get_canopy_cover_conditions(crop,
                                                 landuse_lv1,
                                                 landuse_lv2,
                                                 month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT canopy_cover, source_id, quality_index_id "
                                   F" FROM canopy_cover "
                                   F"WHERE {conds}")

            data = self.db_cursor.fetchall()

            return self.extract_values_sources_quality(data)

        return None

    def get_rougness_conditions(self,
                                crop: Optional[str] = None,
                                landuse_lv1: Optional[str] = None,
                                landuse_lv2: Optional[str] = None,
                                agrotechnology: Optional[str] = None,
                                protection_measure: Optional[str] = None,
                                surface_condition: Optional[str] = None,
                                vegetation_condition: Optional[str] = None,
                                month: Optional[str] = None) -> List[str]:

        conds = []

        if agrotechnology:
            conds.append(f"agrotechnology_id = {agrotechnology}")

        if protection_measure:
            conds.append(f"protection_measure_id = {protection_measure}")

        if surface_condition:
            conds.append(f"surface_condition_id = {surface_condition}")

        if vegetation_condition:
            conds.append(f"vegetation_condition_id = {vegetation_condition}")

        if month:
            conds.append(f"month_id = {month}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

        return conds

    def get_roughness_range(self,
                            crop: Optional[str] = None,
                            landuse_lv1: Optional[str] = None,
                            landuse_lv2: Optional[str] = None,
                            agrotechnology: Optional[str] = None,
                            protection_measure: Optional[str] = None,
                            surface_condition: Optional[str] = None,
                            vegetation_condition: Optional[str] = None,
                            month: Optional[str] = None):

        conds = self.get_rougness_conditions(crop,
                                             landuse_lv1,
                                             landuse_lv2,
                                             agrotechnology,
                                             protection_measure,
                                             surface_condition,
                                             vegetation_condition,
                                             month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            variable_name = "roughness"

            self.db_cursor.execute(
                F"SELECT "
                F"MIN({variable_name}) AS min, "
                F"MAX({variable_name}) AS max, "
                F"AVG({variable_name}) as mean, "
                F"COUNT() as count FROM roughness "
                F"WHERE {conds}")

            return self.check_stat_row(self.db_cursor.fetchall())

        else:
            return self.default_stat_tuple

    def get_roughness_data(self,
                           crop: Optional[str] = None,
                           landuse_lv1: Optional[str] = None,
                           landuse_lv2: Optional[str] = None,
                           agrotechnology: Optional[str] = None,
                           protection_measure: Optional[str] = None,
                           surface_condition: Optional[str] = None,
                           vegetation_condition: Optional[str] = None,
                           month: Optional[str] = None) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:

        conds = self.get_rougness_conditions(crop,
                                             landuse_lv1,
                                             landuse_lv2,
                                             agrotechnology,
                                             protection_measure,
                                             surface_condition,
                                             vegetation_condition,
                                             month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT roughness, source_id, quality_index_id "
                                   F" FROM roughness "
                                   F"WHERE {conds}")

            data = self.db_cursor.fetchall()

            return self.extract_values_sources_quality(data)

        return None

    def get_erodibility_conditions(self,
                                   crop: Optional[str] = None,
                                   landuse_lv1: Optional[str] = None,
                                   landuse_lv2: Optional[str] = None,
                                   ka5_class: Optional[str] = None,
                                   ka5_group_lv1: Optional[str] = None,
                                   ka5_group_lv2: Optional[str] = None,
                                   agrotechnology: Optional[str] = None,
                                   protection_measure: Optional[str] = None,
                                   surface_condition: Optional[str] = None,
                                   month: Optional[str] = None) -> List[str]:

        conds = []

        if ka5_group_lv1:
            conds.append(f"ka5_group_lv1_id = {ka5_group_lv1}")

        if ka5_group_lv2:
            conds.append(f"ka5_group_lv2_id = {ka5_group_lv2}")

        if agrotechnology:
            conds.append(f"agrotechnology_id = {agrotechnology}")

        if protection_measure:
            conds.append(f"protection_measure_id = {protection_measure}")

        if surface_condition:
            conds.append(f"surface_condition_id = {surface_condition}")

        if month:
            conds.append(f"month_id = {month}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

        if ka5_class:
            conds.append(f"ka5_class_id = {ka5_class}")

        return conds

    def get_erodibility_range(self,
                              crop: Optional[str] = None,
                              landuse_lv1: Optional[str] = None,
                              landuse_lv2: Optional[str] = None,
                              ka5_class: Optional[str] = None,
                              ka5_group_lv1: Optional[str] = None,
                              ka5_group_lv2: Optional[str] = None,
                              agrotechnology: Optional[str] = None,
                              protection_measure: Optional[str] = None,
                              surface_condition: Optional[str] = None,
                              month: Optional[str] = None):

        conds = self.get_erodibility_conditions(crop,
                                                landuse_lv1,
                                                landuse_lv2,
                                                ka5_class,
                                                ka5_group_lv1,
                                                ka5_group_lv2,
                                                agrotechnology,
                                                protection_measure,
                                                surface_condition,
                                                month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            variable_name = "erodibility"

            self.db_cursor.execute(
                F"SELECT "
                F"MIN({variable_name}) AS min, "
                F"MAX({variable_name}) AS max, "
                F"AVG({variable_name}) as mean, "
                F"COUNT() as count FROM calibration "
                F"WHERE {conds}")

            return self.check_stat_row(self.db_cursor.fetchall())

        else:
            return self.default_stat_tuple

    def get_erodibility_data(self,
                             crop: Optional[str] = None,
                             landuse_lv1: Optional[str] = None,
                             landuse_lv2: Optional[str] = None,
                             ka5_class: Optional[str] = None,
                             ka5_group_lv1: Optional[str] = None,
                             ka5_group_lv2: Optional[str] = None,
                             agrotechnology: Optional[str] = None,
                             protection_measure: Optional[str] = None,
                             surface_condition: Optional[str] = None,
                             month: Optional[str] = None) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:

        conds = self.get_erodibility_conditions(crop,
                                                landuse_lv1,
                                                landuse_lv2,
                                                ka5_class,
                                                ka5_group_lv1,
                                                ka5_group_lv2,
                                                agrotechnology,
                                                protection_measure,
                                                surface_condition,
                                                month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT erodibility, source_id, quality_index_id "
                                   F" FROM calibration "
                                   F"WHERE {conds}")

            data = self.db_cursor.fetchall()

            return self.extract_values_sources_quality(data)

        return None

    def get_skinfactor_conditions(self,
                                  crop: Optional[str] = None,
                                  landuse_lv1: Optional[str] = None,
                                  landuse_lv2: Optional[str] = None,
                                  ka5_class: Optional[str] = None,
                                  ka5_group_lv1: Optional[str] = None,
                                  ka5_group_lv2: Optional[str] = None,
                                  agrotechnology: Optional[str] = None,
                                  protection_measure: Optional[str] = None,
                                  surface_condition: Optional[str] = None,
                                  month: Optional[str] = None) -> List[str]:

        conds = []

        if ka5_group_lv1:
            conds.append(f"ka5_group_lv1_id = {ka5_group_lv1}")

        if ka5_group_lv2:
            conds.append(f"ka5_group_lv2_id = {ka5_group_lv2}")

        if agrotechnology:
            conds.append(f"agrotechnology_id = {agrotechnology}")

        if protection_measure:
            conds.append(f"protection_measure_id = {protection_measure}")

        if surface_condition:
            conds.append(f"surface_condition_id = {surface_condition}")

        if month:
            conds.append(f"month_id = {month}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

        if ka5_class:
            conds.append(f"ka5_class_id = {ka5_class}")

        return conds


    def get_skinfactor_range(self,
                             crop: Optional[str] = None,
                             landuse_lv1: Optional[str] = None,
                             landuse_lv2: Optional[str] = None,
                             ka5_class: Optional[str] = None,
                             ka5_group_lv1: Optional[str] = None,
                             ka5_group_lv2: Optional[str] = None,
                             agrotechnology: Optional[str] = None,
                             protection_measure: Optional[str] = None,
                             surface_condition: Optional[str] = None,
                             month: Optional[str] = None):

        conds = self.get_skinfactor_conditions(crop,
                                               landuse_lv1,
                                               landuse_lv2,
                                               ka5_class,
                                               ka5_group_lv1,
                                               ka5_group_lv2,
                                               agrotechnology,
                                               protection_measure,
                                               surface_condition,
                                               month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            variable_name = "skinfactor"

            self.db_cursor.execute(
                F"SELECT "
                F"MIN({variable_name}) AS min, "
                F"MAX({variable_name}) AS max, "
                F"AVG({variable_name}) as mean, "
                F"COUNT() as count FROM calibration "
                F"WHERE {conds}")

            return self.check_stat_row(self.db_cursor.fetchall())

        else:
            return self.default_stat_tuple

    def get_skinfactor_data(self,
                            crop: Optional[str] = None,
                            landuse_lv1: Optional[str] = None,
                            landuse_lv2: Optional[str] = None,
                            ka5_class: Optional[str] = None,
                            ka5_group_lv1: Optional[str] = None,
                            ka5_group_lv2: Optional[str] = None,
                            agrotechnology: Optional[str] = None,
                            protection_measure: Optional[str] = None,
                            surface_condition: Optional[str] = None,
                            month: Optional[str] = None) -> Optional[Tuple[List[Any], Dict[str, int], Dict[str, int]]]:

        conds = self.get_skinfactor_conditions(crop,
                                               landuse_lv1,
                                               landuse_lv2,
                                               ka5_class,
                                               ka5_group_lv1,
                                               ka5_group_lv2,
                                               agrotechnology,
                                               protection_measure,
                                               surface_condition,
                                               month)

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT skinfactor, source_id, quality_index_id "
                                   F" FROM calibration "
                                   F"WHERE {conds}")

            data = self.db_cursor.fetchall()

            return self.extract_values_sources_quality(data)

        return None

    def get_initmoisture_range(self,
                               crop: Optional[str] = None,
                               landuse_lv1: Optional[str] = None,
                               landuse_lv2: Optional[str] = None,
                               ka5_class: Optional[str] = None,
                               ka5_group_lv1: Optional[str] = None,
                               ka5_group_lv2: Optional[str] = None,
                               agrotechnology: Optional[str] = None,
                               protection_measure: Optional[str] = None,
                               surface_condition: Optional[str] = None,
                               month: Optional[str] = None):

        conds = []

        if ka5_group_lv1:
            conds.append(f"ka5_group_lv1_id = {ka5_group_lv1}")

        if ka5_group_lv2:
            conds.append(f"ka5_group_lv2_id = {ka5_group_lv2}")

        if month:
            conds.append(f"month_id = {month}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

        if ka5_class:
            conds.append(f"ka5_class_id = {ka5_class}")

        if 0 < len(conds):

            conds = " AND ".join(conds)

            variable_name = "initmoisture"

            self.db_cursor.execute(
                F"SELECT "
                F"MIN({variable_name}) AS min, "
                F"MAX({variable_name}) AS max, "
                F"AVG({variable_name}) as mean, "
                F"COUNT() as count FROM calibration "
                F"WHERE {conds}")

            return self.check_stat_row(self.db_cursor.fetchall())

        else:
            return self.default_stat_tuple

    def check_stat_row(self,
                       rows: List[List[Any]]) -> Tuple[Optional[float], Optional[float],
                                                       Optional[float], Optional[float]]:

        if 0 < len(rows):

            if rows[0][0] is None or \
                    rows[0][1] is None or \
                    rows[0][2] is None:

                return self.default_stat_tuple

            else:

                return rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        else:
            return self.default_stat_tuple
