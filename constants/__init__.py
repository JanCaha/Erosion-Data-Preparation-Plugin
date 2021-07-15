# class TextConstantsEN:
class TextConstants:

    # Layer names

    layer_soil = "soils"
    layer_landuse = "landuse"

    # TableWidgetLanduseAssignedCatalog

    tw_lc_sub_cats = "subcategories"
    tw_lc_col_value = "Source landuse category"
    tw_lc_col_assigned = "Catalogue landuse category"

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
    field_name_sid = "SID"
    field_name_corg = "Corg"

    field_name_d90 = "D90"
    field_name_GB = "GB"

    field_name_k4_code = "k4_code"
    field_name_k4_name = "k4_name"

    field_name_ka5_name = "ka5_name"
    field_name_ka5_code = "ka5_code"
    field_name_ka5_id = "ka5_id"
    field_name_ka5_group_lv2_id = "ka5_group_lv2_id"

    field_name_poly_id = "poly_id"

    field_name_landuse_crops = "landuse_crop"

    field_name_landuse_lv1_id = "landuse_lv1_id"
    field_name_landuse_lv2_id = "landuse_lv2_id"
    field_name_crop_id = "crop_id"
    field_name_crop_name = "crop_name"

    field_name_bulk_density = "Bulk_Density"
    field_name_canopy_cover = "Canopy_Cover"
    field_name_roughness = "Roughness"
    field_name_erodibility = "Erodibility"
    field_name_skinfactor = "Skin_Factor"

    # GUI

    # Main Labels for stackedWidget
    main_labels = ["Set up input data layers",
                   "Soil type class field",
                   "Particle size distribution",
                   "Landuse classification",
                   "Landuse categories",
                   "Organic carbon content (Corg)",
                   "Bulk density",
                   "Canopy cover",
                   "Surface roughness",
                   "Soil erosion resistence",
                   "Skinfactor"
                   ]

    a = """
    
    """

    step_description_labels = [
        "Please select source layers for your landuse and soil properties definition. Both layers need to be polygon geometry vector datasets.\n\nPlease select the digital terrain model that will be used in the model. It will be used for referencing the Erosion-3D input parameter rasters that are going to be generated in the end of this wizard.\n\nAnd set the date when the modeled rainfall event occurs.",
        "Please select the attribute field containing the KA5 (KA4) identifier code. If not present it will be calculated later in the proces from structurall classes contents.",
        "Please assign attribute field from Soils layer containing the pareticle size classes according to the KA5 standard.",
        "Please select attribute field from Landuse layer containing the landuse type and optionaly a crop.",
        "Assign source landuse categories to Erosion-3D Parameters Catalogue categories. For correct quering of the catalogue the landuse categories need to be assigned from values available within the catalogue. Each category can be assigned on different level of classification (don’t miss the „subcategories“ items!)",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        ""
    ]

    label_soil_layer = "Soil properties definition layer:"
    label_landuse_layer = "Landuse definition layer:"
    label_dtm = "DMT layer:"
    label_date = "Event date:"

    label_crop_field = "Landuse field:"
    label_landuse_field = "Crop field:"

    # Tables with widgets

    """Source landuse category	Catalogue landuse category"""

    col_crop = "Crop"
    col_ka5_code = "KA5 Class"
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

    msg_validate_ka5_classes = "Provided column does not contain valid values.\n" \
                               "Values `{missing_values}` are not found amongst KA5 classes in catalog."

    msg_select_all_fields = "All fields must be selected."

    mgs_select_landuse_field = "Landuse field must be selected."

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


class TextConstantsCZ:
    # Layer names

    layer_soil = "soils"
    layer_landuse = "landuse"

    # TableWidgetLanduseAssignedCatalog

    tw_lc_sub_cats = "subcategories"
    tw_lc_col_value = "Value"
    tw_lc_col_assigned = "Assigned value"

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
    field_name_sid = "SID"
    field_name_corg = "Corg"

    field_name_d90 = "D90"
    field_name_GB = "GB"

    field_name_k4_code = "k4_code"
    field_name_k4_name = "k4_name"

    field_name_ka5_name = "ka5_name"
    field_name_ka5_code = "ka5_code"
    field_name_ka5_id = "ka5_id"
    field_name_ka5_group_lv2_id = "ka5_group_lv2_id"

    field_name_poly_id = "poly_id"

    field_name_landuse_crops = "landuse_crop"

    field_name_landuse_lv1_id = "landuse_lv1_id"
    field_name_landuse_lv2_id = "landuse_lv2_id"
    field_name_crop_id = "crop_id"
    field_name_crop_name = "crop_name"

    field_name_bulk_density = "Bulk_Density"
    field_name_canopy_cover = "Canopy_Cover"
    field_name_roughness = "Roughness"
    field_name_erodibility = "Erodibility"
    field_name_skinfactor = "Skin_Factor"

    # GUI

    # Main Labels for stackedWidget
    main_labels = ["Input layers",
                   "Prepared soil KA5 classification:",
                   "Calculate Garbrecht rougness (and possibly KA5 classification)\nfrom structural subclasses content:",
                   "Classify landuse with crops:",
                   "Assign classes to Landuse-Crop pairs:",
                   "Assign values of Corg to data:",
                   "Assign values of Bulk Density to data:",
                   "Assign values of Canopy Cover to data:",
                   "Assign values of Roughness to data:",
                   "Assign values of Erodibility to data:",
                   "Assign values of Skin Factor to data:"
                   ]

    step_description_labels = [
        "Please select source layers for your landuse and soil properties definition. Both layers need to be polygon geometry vector datasets.\nPlease select the digital terrain model that will be used in the model. It will be used for referencing the Erosion-3D input parameter rasters that are going to be generated in the end of this wizard.\nAnd set the date when the modeled rainfall event occurs."
    ]

    # Tables with widgets

    col_crop = "Crop"
    col_ka5_code = "KA5 Class"
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

    msg_validate_ka5_classes = "Provided column does not contain valid values.\n" \
                               "Values `{missing_values}` are not found amongst KA5 classes in catalog."

    msg_select_all_fields = "All fields must be selected."

    mgs_select_landuse_field = "Landuse field must be selected."


# class TextConstants(TextConstantsEN):
#     pass