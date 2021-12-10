from qgis.PyQt import QtCore


class TextConstantsCZ:

    language = "cz"
    locale = QtCore.QLocale(QtCore.QLocale.Czech)

    # Plugin constants

    plugin_name = "E3D+GIS nástroj pro přípravu vstupních parametrů"
    plugin_toolbar_name = "E3D+GIS nástroj pro přípravu vstupních parametrů"
    plugin_toolbar_name_id = "Erosion3DDataPreparationToolbar"

    plugin_main_tool_name = "E3D+GIS nástroj pro přípravu vstupních parametrů"

    plugin_action_name_garbrech_roughness = "Vypočítat Garbrechtovu hydraulickou drsnost"
    plugin_action_id_garbrech_roughness = "GarbrechtRoughness"

    plugin_action_id_process_pour_points = "ProcessPourPoints"
    plugin_action_name_process_pour_points = "Process Pour Points"

    plugin_action_name_empty_wizard = "Vyprázdnit data v hlavním nástroji"

    plugin_action_name_load_data = "Vložit bilanci odnosu půdy do mapy"

    ## Tools

    tool_group_name = "Erosion-3D Data Plugin"
    tool_group_id = "erosiondataplugin"

    tool_gb_name = "Vypočítat Garbrechtovu hydraulickou drsnost ze zrnitostního složení"
    tool_gb_help = "Nástroj vypočítá Garbrechtovu hydraulickou drsnost na základě zrnitostního složení půdy. Průměr zrn D90 je odvozen pro všechny prvky vrstvy z obsahu částic v jednotlivých zrnitostních třídách podle normy KA5."
    tool_gb_input_layer = "Vstupní vrstva se zrnitostním složením:"
    tool_gb_add_d90 = "Zapsat do výstupu hodnoty D90?"
    tool_gb_field_d90 = "Název sloupce pro zapsání D90:"
    tool_gb_field_gr = "Název sloupce pro zapsání drsnosti:"
    tool_gb_output = "Výstupní dataset:"
    tool_gb_ft = "jemný jíl (FT): < 0.0002mm"
    tool_gb_mt = "střední jíl (MT): 0.0002 – 0.00063mm"
    tool_gb_gt = "hrubý jíl (GT): 0.00063 – 0.002mm"
    tool_gb_fu = "jemný prach (FT): 0.002 – 0.0063mm"
    tool_gb_mu = "střední prach (MT): 0.0063 – 0.02mm"
    tool_gb_gu = "hrubý prach (GT): 0.02 – 0.063mm"
    tool_gb_fs = "jemný písek (FT): 0.063 – 0.2mm"
    tool_gb_ms = "střední písek (MT): 0.2 – 0.63mm"
    tool_gb_gs = "hrubý písek (GT): 0.63 – 2.0mm"

    tool_ppp_name = "Zpracovat data ze záznamových bodů"
    tool_ppp_help = "Nástroj převede data ze záznamových bodů (pp_data.csv) do nové struktury pro snazší vytváření hydrogramů a sedimentogramů a přepočte hodnoty výstupů do běžně používaných jednotek (l/s, m3, kg) = Výsledky upravené.\n\nZároveň je možné uložit agregované hodnoty pro celou simulovanou událost (maximální průtok, celkový odtok, celkové množství transportovaného sedimentu) = Výsledky sumarizované.\n\nDo výsledků může být započten pouze plošný povrchový odtok („Runoff“, „Sedvol“ atd.), nebo součet plošného a soustředěného odtoku („ChRunoff“, „ChSedvol“ atd.)"
    tool_ppp_input_data = "Vstupní soubor pp_data.csv:"
    tool_ppp_timestep = "Časový krok simulace [s]:"
    tool_ppp_cellsize = "Velikost buňky rastru [m]:"
    tool_ppp_aggregate_surface_runoff = "Sečíst plošný a soustředěný povrchový odtok?"
    tool_ppp_output_aggregated = "Uložit sumarizované výsledky jako:"
    tool_ppp_output_update = "Uložit upravené výsledky jako:"

    tool_ppp_error = "Názvy sloupců ve vstupním csv neodpovídají požadavkům."

    # Layer names

    layer_soil = "soils"
    layer_landuse = "landuse"
    layer_channel_elements = "channel_elements"
    layer_drain_elements = "drain_elements"

    # main window labels

    text_next = "Další >"
    text_previous = "< Předchozí"

    text_current_step_progress = "Zpracování aktuálního kroku:"

    # TableWidgetLanduseAssignedCatalog

    tw_lc_sub_cats = "dílčí kategorie"
    tw_lc_col_value = "Zdrojová kategorie"
    tw_lcs_col_value = "Zdrojová kategorie"
    tw_lc_col_assigned = "Kategorie Katalogu parametrů"
    tw_lc_col_agrotechnology = "Agrotechnologie"
    tw_lc_col_vegetation_condition = "Stav vegetace"
    tw_lc_col_protection_measure = "Ochranná opatření"
    tw_lc_col_surface_conditions = "Stav povrchu"
    tw_lc_col_detail_level = "Úroveň detailu půd"

    menu_status_ka5 = "třída KA5"
    menu_status_ka5_lv1 = "skupina KA5 1. úrovně"
    menu_status_ka5_lv2 = "skupina KA5 2. úrovně"
    menu_status_ka5_nodifferentiate = "nerozlišovat půdní jednotky"

    # TableWidgetLanduseAssignedValues

    tw_lv_col_value = "Hodnota"
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
    label_steps = "Krok "
    label_from = " z "
    label_dot = "."

    # Main Labels for stackedWidget
    main_labels = ["Zdrojové vrstvy",
                   "Pole půdní třídy",
                   "Zrnitostní složení půd",
                   "Klasifikace využití ploch",
                   "Klasifikace parametrizačních ploch",
                   "Připravené vstupní parametry",
                   "Obah organického uhlíku (Corg)",
                   "Objemová hmotnost půdy",
                   "Zakrytí povrchu rostlinami",
                   "Hydraulická drsnost povrchu",
                   "Erozní odolnost půdy",
                   "Skinfactor",
                   "Volitelné vstupy",
                   "Kontrola a doplnění hodnot",
                   "Uložit vstupní datasety pro Erosion-3D"
                   ]

    step_description_labels = [
        "Vyberte prosím zdrojové vrstvy s definicí půdních vlastností a využití ploch. Obě vrstvy musí být polygonové vektorové datasety.\n\nZvolte vrstvu digitálního modelu povrchu, která bude využita k sestavení modelu v Erosion-3D. Na konci tohoto průvodce bude využita jako referenční rastr pro vytvoření rastrových vstupů Erosion-3D. Tento model terénu by měl být bez dodatečně zahloubených koryt vodních toků. Digitální model terénu obsahující virtuálně zahloubená koryta může být zadán v kroku 13 tohoto průvodce.\n\nZvolte prosím datum, kdy se odehrává simulovaná srážková epizoda.",
        "Vyberte prosím atributové pole obsahující identifikační kód půdní třídy dle normy KA5 (KA4). Pokud nejsou půdy klasifikovány bude klasifikace provedena později ze zrnitostních tříd.\n\nVyberte atributové pole obsahující identifikátor půdních jednotek, který bude využit při tvorbě unikátních kombinací typů využití ploch a zrnitostního složení půdy.",
        "Zvolte prosím atributová pole obsahující zastoupení částic v jednotlivých zrnitostních třídách podle normy KA5. Pokud nemáte podrobné zrnitostní složení pro všech 9 zrnitostních tříd, je možné použít hodnoty celkového obsahu jílu/prachu/písku v zrnitostních třídách Střední jíl (MT)/ Střední prach (MU)/ Střední písek (MS).\n\nPokud si přejete použít střední hodnoty obsahu zrnitostních tříd dle normy KA5 zvolte pro každou zrnitostní třídu odpovídající automaticky vygenerovaná pole „ka5_xx“.",
        "Zvolte prosím atributové pole obsahující typy využití ploch a volitelně pole obsahující plodiny.",
        "Přiřaďte prosím zdrojovým kategoriím využití ploch kategorie odpovídající Katalogu parametrů Erosion-3D. Pro vyhledávání v Katalogu je nutné použít kategorie tak, jak jsou definované v Katalogu. Pro každou z kategorií je možné vícestupňová klasifikace (nepřehlédněte položky „podkategorie“ ve výběru hodnot!)\n\nPokud kategorie mají nějaké speciální charakteristiky (způsob obdělávání, protierozní opatření, stav plodiny) mohou být vybrány z nabízených hodnot a výsledky hledání v katalogu budou odpovídajícím způsobem omezeny.\n\nZvolte úroveň detailu pro členění půdních jednotech (třída > skupina úrovně 2 > skupina úrovně 1). Čím vyšší je úroveň podrobnosti, tím méně lze očekávat výsledků hledání v katalogu. Pokud nejsou pro některou ze tříd parametrizačních ploch nalezeny žádné výsledky, zkuste snížit úroveň detailu členění půd. Pokud zvolíte možnost “nerozlišovat půdní jednotky” budou výsledky hledání pro danou třídu parametrizačních ploch omezeny pouze typem využití a budou mít uniformí půdní vlastnosti.",
        "Hodnoty parametrů již přítomné v některé ze vstupních vrstev mohou být přímo použity bez dalších úprav. Vyhledávání v Katalogu bude pro tyto parametry přeskočeno a do výstupů (tedy vstupních datasetů Erosion-3D) budou přímo přepsány hodnoty ze vstupní vrstvy.\n\nZvolte vstupní vrstvu a její atributové pole s hodnotami daného parametru.",
        "Hodnoty načtené z Katalogu parametrů Erosion-3D pro všechny kombinace využití ploch/plodiny a půdních typů. Hodnoty může upravit, doplnit nebo ponechat prázdné.",
        "Hodnoty načtené z Katalogu parametrů Erosion-3D pro všechny kombinace využití ploch/plodiny a půdních typů. Hodnoty může upravit, doplnit nebo ponechat prázdné.",
        "Hodnoty načtené z Katalogu parametrů Erosion-3D pro všechny kombinace využití ploch/plodiny a půdních typů. Hodnoty může upravit, doplnit nebo ponechat prázdné.",
        "Hodnoty načtené z Katalogu parametrů Erosion-3D pro všechny kombinace využití ploch/plodiny a půdních typů. Hodnoty může upravit, doplnit nebo ponechat prázdné.",
        "Hodnoty načtené z Katalogu parametrů Erosion-3D pro všechny kombinace využití ploch/plodiny a půdních typů. Hodnoty může upravit, doplnit nebo ponechat prázdné.",
        "Hodnoty načtené z Katalogu parametrů Erosion-3D pro všechny kombinace využití ploch/plodiny a půdních typů. Hodnoty může upravit, doplnit nebo ponechat prázdné.",
        "Můžete zadat dodatečné vstupní vrstvy, které budou zahrnuty do přípravy vstupních vrstev pro Erosion-3D.\n\nVrstva „Pour point“ slouží pro vytvoření rastrové vrstvy záznamových bodů, z nichž budou výstupní hodnoty uloženy v tabelované podobě.\n\nPokud chcete použít pro sestavení modelu digitální model terénu s virtuálně zahloubenými koryty vodních toků, zadejte ho zde. V tabulce půdních parametrů bude vytvořena speciální kategorie využití ploch, který je nezávislá na vstupních vrstvách půdních typů a využití ploch. Tato kategorie bude aplikována na buňky u nichž se liší nadmořská výška nebo sklon oproti původnímu DMT zadaném v prvním kroku průvodce. Oba digitální modely terénu musí mít stejnou prostorovou definici. Pokud je tento DMT zadán bude využit pro export v posledním kroku průvodce..\n\n„Odvodňovací prvky“ jsou buňky vstupního rastru využití ploch, které slouží jako „dokonalé odvodnění“, tedy všechen povrchový odtok, který do nich vchází je zcela ztracen (tzn. bezpečně odveden). Odvodňovací prvky mohou být zadány jako bodová nebo liniová geometrie, která bude zahrnuta do výstupního rastru využití ploch a půdních vlastností a tabulky vstupních parametrů jako speciální kategorie.",
        "Zde můžete zkontrolovat a případně manuálně upravit hodnoty pro jednotlivé kombinace využití ploch a skupin půdy.",
        "Data jsou připravena pro export. Zvolte prosím adresáře a jména souborů pro uložení.",
        ""
    ]

    label_soil_layer = "Vrstva s definicí půdních vlastností:"
    label_landuse_layer = "Vrstva s definicí využití ploch:"
    label_dtm = "Vrstva DMT:"
    label_date = "Zvolte datum:"

    label_ka5_class = "KA5 třída:"
    label_soil_id = "Půdní ID:"

    label_crop_field = "Plodiny:"
    label_landuse_field = "Využití ploch:"

    label_initmoisture = "Sloupec obsahující počáteční vlhkost:"
    label_initmoisture_layer = "Vrstva obsahující počáteční vlhkost:  "

    label_bulkdensity = "Sloupec obsahující objemovou hmotnost:"
    label_bulkdensity_layer = "Vrstva obsahující objemovou hmotnost:"

    label_corg = "Sloupec obsahující obsah organického uhlíku:"
    label_corg_layer = "Vrstva obsahující obsah organického uhlíku: "

    label_roughness = "Sloupec obsahující hydraulickou drsnost:"
    label_roughness_layer = "Vrstva obsahující hydraulickou drsnost: "

    label_surfacecover = "Sloupec obsahující zakrytí povrchu:"
    label_surfacecover_layer = "Vrstva obsahující zakrytí povrchu:"

    label_pour_points = "Vrstva záznamových bodů:"
    label_pour_points_identifier = "Atributové pole s identifikátorem bodů:"  # TODO add to GUI
    label_drain_elements = "Odvodňovací prvky:"
    label_channel_elements = "Digitální model terénu se zahloubenými koryty vodních toků:"

    label_data_status_confirm = "Rozumím a chci datasety uložit ve stávajícím stavu."

    label_landuse_raster = "Rastr využití ploch:"
    label_parameter_table = "Tabulka vstupních parametrů:"
    label_lookup_table = "Tabulka propojení:"

    label_created = "Vytvořil <a href=\"https://www.cahik.cz/o-mne/\">Jan Caha</a> pro <a href=\"https://storm.fsv.cvut.cz\">Katedru hydromeliorací a krajinného inženýrství, Fakulta stavební</a>, ČVUT v Praze v roce 2021."
    label_project = "Vývoj byl financován projektem QK1810341 „Vytvoření národní databáze parametrů matematického simulačního modelu Erosion3D a jeho standardizace pro rutinní využití v podmínkách ČR“\nNárodní agentury zemědělského výzkumu České republiky."

    # Tables with widgets

    col_crop = "Plodina"
    col_ka5_code = "Půdní ID (KA5 třída)"
    col_stats = "Statistika"

    header_table_corg = [tw_lcs_col_value, col_crop, col_ka5_code, "", "Corg"]
    header_table_bulkdensity = [tw_lcs_col_value, col_crop, col_ka5_code, "", "Objemová hmotnost půdy"]
    header_table_canopycover = [tw_lcs_col_value, col_crop, "", "Zakrytí povrchu rostlinami"]
    header_table_roughness = [tw_lcs_col_value, col_crop, "", "Hydraulická drsnost povrchu"]
    header_table_erodibility = [tw_lcs_col_value, col_crop, col_ka5_code, "", "Erozní odolnost půdy"]
    header_table_skinfactor = [tw_lcs_col_value, col_crop, col_ka5_code, "", "Skin Factor"]

    message_statistics = "Nalezeno {count} záznamů s rozsahem ({min}, {max}) a průměrem {round(mean, 2)}."
    message_statistics_no_records = "Nalezeno 0 záznamů."

    # Messages

    msg_title = "Chyba v tomto kroku"

    msg_select_layer = "Vrstva musí být vybrána."

    msg_select_soil_id = "Sloupec s ID půdy musí být vybrán."

    msg_validate_ka5_classes = "Zvolený sloupec neobsahuje validní hodnoty.\n" \
                               "Hodnoty `{missing_values}` nelze najít mezi KA5 třídami v katalogu."

    msg_select_all_fields = "Je nutné vybrat pole MT, MU, MS."
    msg_unique_fields = "Každé vybrané pole musí být unikátní."

    msg_select_all_files = "Je nutné zadat všechny cesty pro soubory."

    mgs_select_landuse_field = "Atribut s využitím půdy je nutné vybrat."

    msg_raster_equality = "Vstupní rastr DEM a raster Channel elements nejsou shodné."

    msg_result_data_ok = "Data pro export jsou kompletní."
    msg_result_data_missing = "V tabulce parametrů chybí hodnoty.\nDatasety mohou být uloženy, ale je možné, že budou potřebovat doplnění pro správné sestavení modelu v Erosion-3D."

    # Labels

    label_FT = "Jemný jíl (FT):"
    label_MT = "Střední jíl (MT):"
    label_GT = "Hrubý jíl (GT):"
    label_FU = "Jemný prach (FU):"
    label_MU = "Střední prach (MU):"
    label_GU = "Hrubý prach (GU):"
    label_FS = "Jemný písek (FS):"
    label_MS = "Střední písek (MS):"
    label_GS = "Hrubý písek (GS):"

    dialog_export_label_exported = "Data úspěšně exportována."

    dialog_export_label_exporting = "Data se exportují..."

    dialog_export_label_not_exported = "Data nebyla nastavena k exportu."

    dialog_export_label_not_valid_path = "Cesta pro tento soubor není validní. Data se neexportují."

    dialog_info_label_data_sources = "Zdroje hodnot:"

    dialog_info_label_data_quality = "Kvalita dat:"

    dialog_info_label_histogram = "Histogram hodnot:"

    dialog_info_recods = "záznamů"

    dialog_info_uknown_data_source = "zdroj neuveden (původní německý katalog)"

    dialog_empty_title = "Odstranit data z průvodce"

    dialog_empty_label = "Opravdu odstranit všechna nastavená\ndata z průvodce?"

    information_emptied = "Hodnoty průvodce nastaveny na výchozí stav."

    dialog_load_data_title = "Načíst sedbudget.asc do mapového projektu"

    dialog_load_data_layer = "Vyberte soubor „sedbudget.asc“"

    dialog_load_data_style = "Zvolte symbologii a jednotky"

    dialog_load_data_opacity = "Nastavení průhlednosti"

    dialog_load_data_layer_name = "Název vrstvy"

    dialog_load_data_help = "Nástroj slouží pro načtení výstupního souboru Erosion-3D s hodnotami bilance odnosu půdy („sedbudget.asc“) do mapového projektu s vhodnou symbologií a zvolenou průhledností. Jméno vytvořené vrstvy je odvozeno od jména adresáře, ve které je uložen zdrojový soubor.\n\nHodnoty vrstvy mohou být klasifikovány do 7 nebo 9 tříd a zobrazeny v tunách na hektar nebo kilogramech na metr čtvereční. Zdrojový dataset nebude upraven – jedná se pouze o zobrazení v legendě."

    dialog_load_data_7_cat_tha = "7 kategorií v [t/ha]"
    dialog_load_data_7_cat_kgm2 = "7 kategorií v [kg/m2]"
    dialog_load_data_9_cat_tha = "9 kategorií v [t/ha]"
    dialog_load_data_9_cat_kgm2 = "9 kategorií v [kg/m2]"

    dialog_about_id = "DialogAboutId"

    dialog_about_header = "O tomto plug-inu"

    dialog_about_info = "Verze pluginu {version}, vydaná {day}. {month}. {year}.\n\nVerze katalogu {catalog_version}."

    dialog_about_footer = "Více informací naleznete na <a href=\"https://runoffdb.fsv.cvut.cz\">runoffdb.fsv.cvut.cz</a>."