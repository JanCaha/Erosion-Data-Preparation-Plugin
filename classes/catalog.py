from typing import Optional, List, Dict
from pathlib import Path
import sqlite3


from .singleton import Singleton
from .class_KA5 import KA5Class
from ..constants import TextConstants


class E3dCatalog(metaclass=Singleton):

    def __init__(self,
                 database_file: Optional[str] = None):

        if not database_file or not Path(database_file).exists():
            database_file = "database.sqlite"
            self.database_file = Path(__file__).parent.parent / "db_catalog" / database_file

        else:
            self.database_file = Path(database_file)

        self.db_connection = sqlite3.connect(self.database_file)

        self.db_cursor = self.db_connection.cursor()

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

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id, landuse_lv1_id FROM landuse_lv2")

        rows = self.db_cursor.fetchall()

        # count += len(rows)

        for row in rows:
            data.update({row[0]: LanduseCrop(object_id=row[1],
                                             name=row[0],
                                             table="landuse_lv2",
                                             id_landuse_lv1=row[2],
                                             id_landuse_lv2=row[1],
                                             id_crop=None)})

        self.db_cursor.execute(f"SELECT name_{TextConstants.language}, id, landuse_lv2_id FROM crop")

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

        self.db_cursor.execute(f"SELECT id, code, name_{TextConstants.language}, ka5_group_lv2_id, "
                               f"ft, mt, gt, fu, mu, gu, fs, ms, gs FROM ka5_class")

        rows = self.db_cursor.fetchall()

        for row in rows:
            classes.append(KA5Class.from_array(row))

        return classes

    def get_bulk_density_range(self,
                               ka5_class: Optional[str] = None,
                               ka5_group_lv2: Optional[str] = None,
                               crop: Optional[str] = None,
                               landuse_lv1: Optional[str] = None,
                               landuse_lv2: Optional[str] = None,
                               agrotechnology: Optional[str] = None,
                               month: Optional[str] = None):

        conds = []

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

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT MIN(bulk_density) AS min, MAX(bulk_density) AS max, "
                                   F"AVG(bulk_density) AS mean, COUNT() AS count FROM bulk_density "
                                   F"WHERE {conds}")

            rows = self.db_cursor.fetchall()

            if 0 < len(rows):
                return rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        else:
            return None, None, None, 0

    def get_corg_range(self,
                       ka5_class: Optional[str] = None,
                       ka5_group_lv2: Optional[str] = None,
                       crop: Optional[str] = None,
                       landuse_lv1: Optional[str] = None,
                       landuse_lv2: Optional[str] = None,
                       agrotechnology: Optional[str] = None):

        conds = []

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

        if 0 < len(conds):

            conds = " AND ".join(conds)

            self.db_cursor.execute(F"SELECT MIN(corg) AS min, MAX(corg) AS max, AVG(corg) as mean, COUNT() as count FROM corg "
                                   F"WHERE {conds}")

            rows = self.db_cursor.fetchall()

            if 0 < len(rows):
                return rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        else:
            return None, None, None, 0

    def get_canopy_cover_range(self,
                               crop: Optional[str] = None,
                               landuse_lv1: Optional[str] = None,
                               landuse_lv2: Optional[str] = None,
                               month: Optional[str] = None):

        conds = []

        if month:
            conds.append(f"month_id = {month}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

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

            rows = self.db_cursor.fetchall()

            if 0 < len(rows):
                return rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        else:
            return None, None, None, 0

    def get_roughness_range(self,
                            crop: Optional[str] = None,
                            landuse_lv1: Optional[str] = None,
                            landuse_lv2: Optional[str] = None,
                            agrotechnology: Optional[str] = None,
                            protection_measure: Optional[str] = None,
                            surface_condition: Optional[str] = None,
                            vegetation_condition: Optional[str] = None,
                            month: Optional[str] = None):
        conds = []

        if month:
            conds.append(f"month_id = {month}")

        if crop:
            conds.append(f"crop_id = {crop}")

        if landuse_lv1:
            conds.append(f"landuse_lv1_id = {landuse_lv1}")

        if landuse_lv2:
            conds.append(f"landuse_lv2_id = {landuse_lv2}")

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

            rows = self.db_cursor.fetchall()

            if 0 < len(rows):
                return rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        else:
            return None, None, None, 0

    def get_erodibility_range(self,
                              crop: Optional[str] = None,
                              landuse_lv1: Optional[str] = None,
                              landuse_lv2: Optional[str] = None,
                              ka5_class: Optional[str] = None,
                              ka5_group_lv2: Optional[str] = None,
                              agrotechnology: Optional[str] = None,
                              protection_measure: Optional[str] = None,
                              surface_condition: Optional[str] = None,
                              month: Optional[str] = None):

        conds = []

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

            variable_name = "erodibility"

            self.db_cursor.execute(
                F"SELECT "
                F"MIN({variable_name}) AS min, "
                F"MAX({variable_name}) AS max, "
                F"AVG({variable_name}) as mean, "
                F"COUNT() as count FROM calibration "
                F"WHERE {conds}")

            rows = self.db_cursor.fetchall()

            if 0 < len(rows):
                return rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        else:
            return None, None, None, 0

    def get_skinfactor_range(self,
                             crop: Optional[str] = None,
                             landuse_lv1: Optional[str] = None,
                             landuse_lv2: Optional[str] = None,
                             ka5_class: Optional[str] = None,
                             ka5_group_lv2: Optional[str] = None,
                             agrotechnology: Optional[str] = None,
                             protection_measure: Optional[str] = None,
                             surface_condition: Optional[str] = None,
                             month: Optional[str] = None):

        conds = []

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

            variable_name = "skinfactor"

            self.db_cursor.execute(
                F"SELECT "
                F"MIN({variable_name}) AS min, "
                F"MAX({variable_name}) AS max, "
                F"AVG({variable_name}) as mean, "
                F"COUNT() as count FROM calibration "
                F"WHERE {conds}")

            rows = self.db_cursor.fetchall()

            if 0 < len(rows):
                return rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        else:
            return None, None, None, 0

    def get_initmoisture_range(self,
                               crop: Optional[str] = None,
                               landuse_lv1: Optional[str] = None,
                               landuse_lv2: Optional[str] = None,
                               ka5_class: Optional[str] = None,
                               ka5_group_lv2: Optional[str] = None,
                               agrotechnology: Optional[str] = None,
                               protection_measure: Optional[str] = None,
                               surface_condition: Optional[str] = None,
                               month: Optional[str] = None):

        conds = []

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

            rows = self.db_cursor.fetchall()

            if 0 < len(rows):
                return rows[0][0], rows[0][1], rows[0][2], rows[0][3]

        else:
            return None, None, None, 0
