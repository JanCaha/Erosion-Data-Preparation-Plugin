from typing import Optional, List, Any

from .catalog import E3dCatalog


class LanduseCrop:

    __slots__ = ["catalog", "id", "name", "table", "id_landuse_lv1", "id_landuse_lv2", "id_crop"]

    def __init__(self,
                 object_id: str,
                 name: str,
                 table: str,
                 id_landuse_lv1: str,
                 id_landuse_lv2: Optional[str],
                 id_crop: Optional[str]):

        self.catalog = E3dCatalog()

        self.id = object_id
        self.name = name
        self.table = table
        self.id_landuse_lv1 = id_landuse_lv1
        self.id_landuse_lv2 = id_landuse_lv2
        self.id_crop = id_crop

    def __repr__(self):
        return f"LanduseCrop for {self.name} from table {self.table}."

    def get_fields_for_layer(self) -> List[Any]:

        values = self.catalog.get_values("calibration", self.id_landuse_lv1, self.id_landuse_lv2, self.id_crop)

        if values:
            return [values[0], values[1], values[2], values[3], values[4], values[5]]

        else:

            # return [self.name, self.bulk_density, self.init_moisture, self.erodibility,
            #         self.roughness, self.cover, self.skin_factor]
            return [None, None, None, None, None, None]
