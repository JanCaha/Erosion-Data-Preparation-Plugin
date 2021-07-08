class TextConstants:

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

    main_labels = ["Set up input data layers:",
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
