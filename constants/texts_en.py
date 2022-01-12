from qgis.PyQt import QtCore


class TextConstantsEN:
    language = "en"
    locale = QtCore.QLocale(QtCore.QLocale.English)

    # Plugin constants

    plugin_name = "E3D+GIS input parameters preparation tool"
    plugin_toolbar_name = "E3D+GIS input parameters preparation tool Toolbar"
    plugin_toolbar_name_id = "Erosion3DDataPreparationToolbar"

    plugin_main_tool_name = "E3D+GIS input parameters preparation Wizard"

    plugin_main_window_name = "Erosion-3D data preparation wizard"
    
    plugin_action_name_garbrech_roughness = "Calculate Garbrecht roughness"
    plugin_action_id_garbrech_roughness = "GarbrechtRoughness"

    plugin_action_id_process_pour_points = "ProcessPourPoints"
    plugin_action_name_process_pour_points = "Process Pour Point data"
    
    plugin_action_name_empty_wizard = "Empty data in wizard"

    plugin_action_name_load_data = "Load sediment budget into current map"

    ## Tools

    tool_group_name = "Erosion-3D Data Plugin"
    tool_group_id = "erosiondataplugin"

    tool_gb_name = "Calculate Garbrecht hydraulic roughness from particle size distribution"
    tool_gb_help = "The tool calculates Garbrecht’s hydraulic rougness from the particle size distribution. The D90 particle diameter is derived for all features in the input layer from provided soil particle size classes content according to KA5 standard."
    tool_gb_input_layer = "Input layer containing the particle size class contents:"
    tool_gb_add_d90 = "Write the D90 values to output?"
    tool_gb_field_d90 = "Attribute field to store the D90 values:"
    tool_gb_field_gr = "Attribute field to store the roughness values:"
    tool_gb_output = "Output feature class:"
    tool_gb_ft = "Fine clay (FT): < 0.0002mm"
    tool_gb_mt = "Medium clay (MT): 0.0002 – 0.00063mm"
    tool_gb_gt = "Course clay (GT): 0.00063 – 0.002mm"
    tool_gb_fu = "Fine silt (FT): 0.002 – 0.0063mm"
    tool_gb_mu = "Medium silt (MT): 0.0063 – 0.02mm"
    tool_gb_gu = "Course silt (GT): 0.02 – 0.063mm"
    tool_gb_fs = "Fine sand (FT): 0.063 – 0.2mm"
    tool_gb_ms = "Medium sand (MT): 0.2 – 0.63mm"
    tool_gb_gs = "Course sand (GT): 0.63 – 2.0mm"

    tool_ppp_name = "Process Pour Point data"
    tool_ppp_help = "The tool transforms the pour point record (pp_data.csv) to an alternative structure more suitable for hydrographs and sedigraphs ploting. The results are recalculated to commonly used units (l/s, m3, kg) = Results converted\n\nSumarized values for the whole simulated event may saved as well (maximum discharge rate, total runoff volume, total sediment mass) = Sumarized results\n\nOnly sheet flow values may be saved („Runoff“, „Sedvol“ etc.) or combined values of channel and sheet flow („ChRunoff“, „ChSedvol“ etc.)"
    tool_ppp_input_data = "Input pp_data.csv file:"
    tool_ppp_timestep = "Simulation timestep [s]:"
    tool_ppp_cellsize = "DEM raster cell size [m]:"
    tool_ppp_aggregate_surface_runoff = "Sumarize sheet and channel flow?"
    tool_ppp_output_aggregated = "Save sumarized results as:"
    tool_ppp_output_update = "Save transformed results as:"

    tool_ppp_error = "Header of csv file does not match requirements."

    # Layer names

    layer_soil = "soils"
    layer_landuse = "landuse"
    layer_channel_elements = "channel_elements"
    layer_drain_elements = "drain_elements"

    # main window labels

    text_next = "Next >"
    text_previous = "< Previous"

    text_current_step_progress = "Current step processing:"

    # TableWidgetLanduseAssignedCatalog

    tw_lc_sub_cats = "subcategories"
    tw_lc_col_value = "Source landuse category"
    tw_lcs_col_value = "Landuse category"
    tw_lc_col_assigned = "Catalogue landuse category"
    tw_lc_col_agrotechnology = "Agrotechnology"
    tw_lc_col_vegetation_condition = "Vegetation condition"
    tw_lc_col_protection_measure = "Protection measure"
    tw_lc_col_surface_conditions = "Surface conditions"
    tw_lc_col_detail_level = "Soil detail level"

    menu_status_ka5 = "KA5 Class"
    menu_status_ka5_lv1 = "KA5 group level 1"
    menu_status_ka5_lv2 = "KA5 group level 2"
    menu_status_ka5_nodifferentiate = "don’t differentiate"

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
    field_name_ka5_group_lv1_id = "ka5_group_lv1_id"

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
                   "Parametrization patches classification",
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
        "Please select source layers for your landuse and soil properties definition. Both layers need to be polygon geometry vector datasets.\n\nPlease select the digital terrain model that will be used in the model. It will be used for referencing the Erosion-3D input parameter rasters that are going to be generated in the end of this wizard. This DEM should be without streams burnt-in. If you’d like to use DEM with burnt-in stream channels you may specify it in step 13. \n\nAnd set the date when the modeled rainfall event occurs.",
        "Please select the attribute field containing the KA5 (KA4) identifier code. If not present it will be calculated later in the proces from structurall classes contents.\n\nSelect the attribute field with your arbitrary soil units identifier which will be used for definition of unique combinations of landuse and soil texture.",
        "Please assign attribute field from Soils layer containing the pareticle size classes according to the KA5 standard. If you don’t have the detailed textural classes content you may assign total of clay/silt/sand particles to the Medium clay (MT)/ Medium silt (MU)/ Medium sand (MS).\n\nIf your soils are allready classified to KA5 you may also use the average values provided in the standard. In that case assign to all of the attribute field the generated field „ka5_xx“.",
        "Please select attribute field from Landuse layer containing the landuse type and optionaly a crop.",
        "Assign source landuse categories to Erosion-3D Parameters Catalogue categories. For correct quering of the catalogue the landuse categories need to be assigned from values available within the catalogue. Each category can be assigned on different level of classification (don’t miss the „subcategories“ items!)\nIf the categories include any special limitations (agrotechnology, soil erosion protection measures, vegetation condition) you may specify them too and the query will be limited accordingly.\n\nSet the level of detail for soil classes classification (class > group level 2 > group level 1). Higher the level of detail lower the the number of results will be. You can try to reduce the level of detail if no results are found for a parametrization patch class. The „don’t differentiate“ option will completely ignore the soil definition geometry and the landuse category will have uniform properties.\n\nThis step is crucial for following steps and returning here from further stages of this wizzard will discard all manual editing of the parametres (i.e. all the values will be loaded again from the catalogue).",
        "Parameter values that have been allready prepared in an input layer may used without further processing. Retrieving values from the Catalogue will be skipped for those parameters and values from selected field will be directly transcripted into the outputs (i.e. input parameter datasets for Erosion-3D).\n\nSelect the source layer and attribute field for each of the prepared parameters.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "The values loaded from the Erosion-3D Parameters Catalogue for each combination of landuse/crop and soil type. Adjust the values as desired or leave blank.",
        "Please specify additional input layers to be included in the processing of the Erosion-3D input datasets.\n\nPour point layer serves for deriving correct raster definition of DEM cells where the tabelated outputs of Erosion3D are recorded.\n\nIf digital elevation model with burnt-in channels is used you can specify it here. This input will be used to create one special landuse category that is independent of the input soil and landuse layers. This category will be applied on pixels where the elevation or inclination differs compared to the original DEM. Both elevation rasters must have the same spatial definition. This DEM will be experted in the last step if set here.\n\nDrain elements are raster cells that drain any surface runoff completely. Please select point or line feature layer that will be converted into raster layer with special category in the soil parameters table.",
        "Here you can check the values before the export. The values can be manually adjusted if desired.",
        "Data for export is complete. Please select the input files you want to export and set name and directory to store them to.",
        ""
    ]

    label_soil_layer = "Soil properties definition layer:"
    label_landuse_layer = "Landuse definition layer:"
    label_dtm = "DEM layer:"
    label_date = "Event date:"

    label_ka5_class = "KA5 class:"
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
    label_pour_points_identifier = "Pour points identifier field:"  # TODO add to GUI
    label_drain_elements = "Drain features points or lines:"
    label_channel_elements = "DEM with channels:"

    label_data_status_confirm = "I understand and want to proceed anyway."

    label_landuse_raster = "Landuse raster:"
    label_parameter_table = "Parameters table:"
    label_lookup_table = "Lookup table:"

    label_created = "Developed by <a href=\"https://www.cahik.cz/o-mne/\">Jan Caha</a> for <a href=\"https://storm.fsv.cvut.cz\">Department of Landscape Water Conservation, Faculty of Civil Engineering</a>, Czech Technical University in Prague in 2021."
    label_project = "Development of this plug-in was financed by project No. QK1810341 „Creating a national database of parameters\nfor the mathematical simulation model EROSION-3D and its standardization for routine use in the Czech Republic“ of the National Agency of Agricultural Research of Czech Republic."

    # Tables with widgets

    col_crop = "Crop"
    col_ka5_code = "Soil ID (KA5 Class)"
    col_stats = "Statistics"

    header_table_corg = [tw_lcs_col_value, col_crop, col_ka5_code, "", "Corg"]
    header_table_bulkdensity = [tw_lcs_col_value, col_crop, col_ka5_code, "", "Bulk Density"]
    header_table_canopycover = [tw_lcs_col_value, col_crop, "", "Canopy Cover"]
    header_table_roughness = [tw_lcs_col_value, col_crop, "", "Roughness"]
    header_table_erodibility = [tw_lcs_col_value, col_crop, col_ka5_code, "", "Erodibility"]
    header_table_skinfactor = [tw_lcs_col_value, col_crop, col_ka5_code, "", "Skin Factor"]

    message_statistics = "Found {count} records with range ({min}, {max}) and mean {round(mean, 2)}."
    message_statistics_no_records = "Found 0 records."

    # Messages

    msg_title = "Error in this step"

    msg_select_layer = "Layer must be selected."

    msg_select_soil_id = "Soil ID field must be selected."

    msg_validate_ka5_classes = "Provided column does not contain valid values.\n" \
                               "Values `{missing_values}` are not found amongst KA5 classes in catalog."

    msg_select_all_fields = "Field MT, MU, MS must be selected."
    msg_unique_fields = "Every selected field must be unique."

    msg_select_all_files = "All file paths must be specified."

    mgs_select_landuse_field = "Landuse field must be selected."

    msg_raster_equality = "Input DEM raster and Channel elements raster are not equal."

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

    dialog_export_label_exported = "Data successfully exported."

    dialog_export_label_exporting = "Exporting data..."

    dialog_export_label_not_exported = "Dataset not set up for export."

    dialog_export_label_not_valid_path = "Path for this dataset is not valid. Data not exported."

    dialog_info_label_data_sources = "Data Sources:"

    dialog_info_label_data_quality = "Data Quality:"

    dialog_info_label_histogram = "Data Histogram:"

    dialog_info_recods = "records"

    dialog_info_uknown_data_source = "data source unknown (original german parameters catalogue)"

    dialog_empty_title = "Empty data from wizard"

    dialog_empty_label = "Really remove all preset data\nfrom plugin wizard?"

    information_emptied = "Wizard values emptied."

    dialog_load_data_title = "Load sedbudget.asc into map project"

    dialog_load_data_layer = "Select file"

    dialog_load_data_style = "Select symbology"

    dialog_load_data_opacity = "Transparency"

    dialog_load_data_layer_name = "Layer name"

    dialog_load_data_help = "The tool loads the Erosion-3D output raster „sedbudget.asc“ into current map project with suitable symbology and desired transparency.\n\nDefault name of the created map layer is composed from parent directory name of selected sedbudget.asc file.\n\nThe values can by classified into 7 or 9 classes and displayed in tonnes per hactare or kilograms per square meter. The values of the layer are not recalculated only the legend description is adjusted according to selected item."

    dialog_load_data_7_cat_tha = "7 categories in [t/ha]"
    dialog_load_data_7_cat_kgm2 = "7 categories in [kg/m2]"
    dialog_load_data_9_cat_tha = "9 categories in [t/ha]"
    dialog_load_data_9_cat_kgm2 = "9 categories in [kg/m2]"

    dialog_about_id = "DialogAboutId"

    dialog_about_header = "About this plug-in"

    dialog_about_info = "Plugin version {version}, released on {day}. {month}. {year}.\n\nCatalogue version {catalog_version}."

    dialog_about_footer = "More information at <a href=\"https://runoffdb.fsv.cvut.cz\">runoffdb.fsv.cvut.cz</a>."
