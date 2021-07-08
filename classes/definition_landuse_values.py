from typing import Optional, List, Any


class LanduseValues:

    __slots__ = ["name", "bulk_density", "init_moisture", "erodibility", "roughness", "cover", "skin_factor"]

    def __init__(self,
                 name: str,
                 bulk_density: float,
                 init_moisture: float,
                 erodibility: float,
                 roughness: float,
                 cover: float,
                 skin_factor: float):

        self.name = name
        self.bulk_density = bulk_density
        self.init_moisture = init_moisture
        self.erodibility = erodibility
        self.roughness = roughness
        self.cover = cover
        self.skin_factor = skin_factor

    def __repr__(self):
        return f"LanduseValues for {self.name} with values ({self.bulk_density}, {self.init_moisture}, ...)."

    def check_none_values(self):
        return self.bulk_density is None or \
            self.init_moisture is None or \
            self.erodibility is None or \
            self.roughness is None or \
            self.cover is None or \
            self.skin_factor is None

    def get_fields_for_layer(self) -> List[Any]:
        return [self.name, self.bulk_density, self.init_moisture, self.erodibility,
                self.roughness, self.cover, self.skin_factor]