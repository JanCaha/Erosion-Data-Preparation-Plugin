import os
from pathlib import Path

from osgeo import ogr, gdal

conn_string = "MYSQL:testcatalog,user=root,password=root,host=localhost,port=3306"

mysql_ds: ogr.DataSource = ogr.Open(conn_string)

print(mysql_ds.GetLayerCount())


driver: ogr.Driver = ogr.GetDriverByName("SQLite")

path = Path(__file__).parent / "database.sqlite"

print(path.absolute())

ds: ogr.DataSource = driver.CreateDataSource(str(path.absolute()))

for i in range(mysql_ds.GetLayerCount()):

    layer: ogr.Layer = mysql_ds.GetLayerByIndex(i)

    print(F" - {i} : {layer.GetName()}")

    ds.CopyLayer(layer, layer.GetName(), options=["FID=id"])
