from PyQt5 import QtCore


# class TextConstantsEN:
class TextConstants:

    language = "en"
    locale = QtCore.QLocale(QtCore.QLocale.English)

    # Plugin constants

    plugin_name = "Erosion-3D Data Preparation"
    plugin_toolbar_name = "Erosion-3D Data Preparation Toolbar"
    plugin_toolbar_name_id = "Erosion3DDataPreparationToolbar"

    plugin_main_tool_name = "Erosion-3D Data Preparation Wizard"

    plugin_action_name_garbrech_roughness = "Garbrecht Roughness"
    plugin_action_id_garbrech_roughness = "GarbrechtRoughness"

    ## Tools

    tool_group_name = "Erosion-3D Data Plugin"
    tool_group_id = "erosiondataplugin"

    # Layer names

    layer_soil = "soils"
    layer_landuse = "landuse"
    layer_channel_elements = "channel_elements"
    layer_drain_elements = "drain_elements"

    # TableWidgetLanduseAssignedCatalog

    tw_lc_sub_cats = "subcategories"
    tw_lc_col_value = "Source landuse category"
    tw_lc_col_assigned = "Catalogue landuse category"
    tw_lc_col_agrotechnology = "Agrotechnology"
    tw_lc_col_vegetation_condition = "Vegetation condition"
    tw_lc_col_protection_measure = "Protection measure"
    tw_lc_col_surface_conditions = "Surface conditions"

    # TableWidgetLanduseAssignedValues

    tw_lv_col_value = "Value"
    tw_lv_col_bulkdensity = "bulkdensity"
    tw_lv_col_initmoisture = "initmoisture"
    tw_lv_col_erodibility = "erodibility"
    tw_lv_col_roughn = "roughn"
    tw_lv_col_cover = "cover"
    tw_lv_col_skinfactor = "skinfactor"

    # QgsVectorLayer for join

    vl_join_col_name = "name"

    # field names
    field_name_fid = "POLY_NR"

    field_name_soil_id = "Soil_ID"

    field_name_d90 = "D90"
    field_name_GB = "GB"

    field_name_month = "month"

    field_name_k4_code = "k4_code"
    field_name_k4_name = "k4_name"

    field_name_ka5_name = "ka5_name"
    field_name_ka5_code = "ka5_code"
    field_name_ka5_id = "ka5_id"
    field_name_ka5_group_lv2_id = "ka5_group_lv2_id"

    field_name_poly_id = "POLY_ID"

    field_name_landuse_crops = "landuse_crop"

    field_name_landuse_lv1_id = "landuse_lv1_id"
    field_name_landuse_lv2_id = "landuse_lv2_id"
    field_name_crop_id = "crop_id"
    field_name_crop_name = "crop_name"

    field_name_agrotechnology = "agrotechnology"
    field_name_vegetation_conditions = "vegetation_conditions"
    field_name_protection_measure = "protection_measure"
    field_name_surface_conditions = "surface_conditions"

    field_name_corg = "CORG"
    field_name_bulk_density = "BLKDENSITY"
    field_name_canopy_cover = "COVER"
    field_name_roughness = "ROUGHNESS"
    field_name_erodibility = "ERODIBIL"
    field_name_skinfactor = "SKINFACTOR"
    field_name_init_moisture = "INITMOIST"

    field_name_FT = "FT"
    field_name_MT = "MT"
    field_name_GT = "GT"
    field_name_FU = "FU"
    field_name_MU = "MU"
    field_name_GU = "GU"
    field_name_FS = "FS"
    field_name_MS = "MS"
    field_name_GS = "GS"

    field_name_layer_id = "LAYER_ID"
    field_name_layer_thick = "LAYERTHICK"

    # GUI
    label_steps = "Step "
    label_from = " from "
    label_dot = "."

    # Main Labels for stackedWidget
    main_labels = ["Set up input data layers",
                   "Soil type class field",
                   "Particle size distribution",
                   "Landuse classification",
                   "Landuse categories",
                   "Prepared inputs sources",
                   "Organic carbon content (Corg)",
                   "Bulk density",
                   "Canopy cover",
                   "Surface roughness",
                   "Soil erosion resistence",
                   "Skinfactor",
                   "Optional inputs",
                   "Final check and adjustments",
                   "Export input datasets for Erosion-3D"
                   ]


    step_description_labels = [
        "Please select source layers for your landuse and soil properties definition. Both layers need to be polygon geometry vector datasets.\n\nPlease select the digital terrain model that will be used in the model. It will be used for referencing the Erosion-3D input parameter rasters that are going to be generated in the end of this wizard.\n\nAnd set the date when the modeled rainfall event occurs.",
        "Please select the attribute field containing the KA5 (KA4) identifier code. If not present it will be calculated later in the proces from structurall classes contents.\n\nSelect the attribute field with your arbitrary soil units identifier which will be used for definition of unique combinations of landuse and soil texture.",
        "Please assign attribute field from Soils layer containing the pareticle size classes according to the KA5 standard.",
        "Please select attribute field from Landuse layer containing the landuse type and optionaly a crop.",
        "Assign source landuse categories to Erosion-3D Parameters Catalogue categories. For correct quering of the catalogue the landuse categories need to be assigned from values available within the catalogue. Each category can be assigned on different level of classification (don’t miss the „subcategories“ items!)\nIf the categories include any special limitations (agrotechnology, soil erosion protection measures, vegetation condition) you may specify them too and the query will be limited accordingly.",
        "Parameter values that have been allready prepared in an input layer may used without further processing. Retrieving values from the Catalogue will be skipped for those parameters and values from selected field will be directly transcripted into the outputs (i.e. input parameter datasets for Erosion-3D).\n\nSelect the source layer and attribute field for each of the prepared parameters.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "Please specify additional input layers to be included in the processing of the Erosion-3D input datasets.\n\nPour point layer serves for deriving correct raster definition of DMT cells where the tabelated outputs of Erosion3D are recorded.\n\nChannel elements is a raster layer that defines cells of „stream flow“ in the simulation. This input may be used to create one special landuse category that is independent of the input soil and landuse layers. The layer is a raster that must have the same spatial definition as the DMT. The channel elements raster generated by Erosion-3D during the Relief dataset processing can be used.\n\nDrain elements are raster cells that drain any surface runoff completely. Please select point or line feature layer that will be converted into raster layer with special category in the soil parameters table.",
        "Here you can check the values before the export. The values can be manually adjusted if desired.",
        "Data for export is complete. Please select the input files you want to export and set name and directory to store them to.",
        ""
    ]

    label_soil_layer = "Soil properties definition layer:"
    label_landuse_layer = "Landuse definition layer:"
    label_dtm = "DMT layer:"
    label_date = "Event date:"

    label_ka5_class ="KA5 class:"
    label_soil_id = "Soil ID:"

    label_crop_field = "Crop field:"
    label_landuse_field = "Landuse field:"

    label_initmoisture = "Initial moisture attribute field:"
    label_initmoisture_layer = "Initial moisture from layer:"

    label_bulkdensity = "Bulk density attribute field:"
    label_bulkdensity_layer = "Bulk density from layer:"

    label_corg = "Organic carbon content attribute field:"
    label_corg_layer = "Organic carbon content from layer:"

    label_roughness = "Manning roughness attribute field:"
    label_roughness_layer = "Manning roughness from layer:"

    label_surfacecover = "Surface cover attribute field:"
    label_surfacecover_layer = "Surface cover from layer: "

    label_pour_points = "Pour point feature layer:"
    label_pour_points_identifier = "Pour points identifier field:" # TODO add to GUI
    label_drain_elements = "Drain features points or lines:"
    label_channel_elements = "Channel elements:"

    label_data_status_confirm = "I understand and want to proceed anyway."

    label_landuse_raster = "Landuse raster:"
    label_parameter_table = "Parameters table:"
    label_lookup_table = "Lookup table:"

    label_created = "Developed by <a href=\"https://www.cahik.cz/o-mne/\">Jan Caha</a> for Department of Landscape Water Conservation, Faculty of Civil Engineering, Czech Technical University in Prague in 2021."
    label_project = "Development of this plug-in was financed by project No. QK1810341 „Creating a national database of parameters for the mathematical simulation model EROSION-3D and its standardization for routine use in the Czech Republic“ of the National Agency of Agricultural Research of Czech Republic."

    # Tables with widgets

    col_crop = "Crop"
    col_ka5_code = "Soil ID (KA5 Class)"
    col_stats = "Statistics"

    header_table_corg = [col_crop, col_ka5_code, "Corg from catalog", "Corg"]
    header_table_bulkdensity = [col_crop, col_ka5_code, "Bulk Density from catalog", "Bulk Density"]
    header_table_canopycover = [col_crop, "Canopy Cover from catalog", "Canopy Cover"]
    header_table_roughness = [col_crop, "Roughness from catalog", "Roughness"]
    header_table_erodibility = [col_crop, col_ka5_code, "Erodibility from catalog", "Erodibility"]
    header_table_skinfactor = [col_crop, col_ka5_code, "Skin Factor from catalog", "Skin Factor"]

    message_statistics = "Found {count} records with range ({min}, {max}) and mean {round(mean, 2)}."
    message_statistics_no_records = "Found 0 records."

    # Messages

    msg_title = "Error in this step"

    msg_select_layer = "Layer must be selected."

    msg_select_soil_id = "Soil ID field must be selected."

    msg_validate_ka5_classes = "Provided column does not contain valid values.\n" \
                               "Values `{missing_values}` are not found amongst KA5 classes in catalog."

    msg_select_all_fields = "All fields must be selected."

    msg_select_all_files = "All file paths must be specified."

    mgs_select_landuse_field = "Landuse field must be selected."

    msg_result_data_ok = "Data for export is complete."
    msg_result_data_missing = "Parameters table is missing some values.\nThe datasets can be saved anyway but they may need some more processing to be used in Erosion-3D."

    # Labels

    label_FT = "Fine clay(FT):"
    label_MT = "Medium clay(MT):"
    label_GT = "Coarse clay(GT):"
    label_FU = "Fine silt (FU):"
    label_MU = "Medium silt (MU):"
    label_GU = "Coarse silt (GU):"
    label_FS = "Fine sand (FS):"
    label_MS = "Medium sand (MS):"
    label_GS = "Coarse sand (GS):"

# class TextConstants(TextConstantsEN):
#     pass