from typing import Tuple, List, Any
import inspect
import unicodedata


from qgis.core import (QgsMessageLog,
                       Qgis,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsProject,
                       QgsMapLayer,
                       NULL)

from ..constants import TextConstants


def eval_string_with_variables(input_string: str) -> str:

    parent_frame = inspect.currentframe().f_back.f_locals

    for key, value in parent_frame.items():
        if "__" not in key:
            if isinstance(value, str):
                exec(F"{key} = '{value}'")
            elif isinstance(value, float) or \
                    isinstance(value, int) or \
                    isinstance(value, bool) or \
                    isinstance(value, list) or \
                    isinstance(value, dict):
                exec(F"{key} = {value}")

    return eval(f'f"""{input_string}"""')


def recode_2_ascii(unicode_string: str) -> str:
    return unicodedata.normalize('NFKD', unicode_string).\
        encode('ascii', 'ignore').\
        decode("ascii").\
        replace(" ", "_")


def add_maplayer_to_project(layer: QgsMapLayer):

    QgsProject.instance().addMapLayer(layer)


def log(text):
    QgsMessageLog.logMessage(str(text),
                             TextConstants.plugin_name,
                             Qgis.Info)


def evaluate_data_completeness(layer: QgsVectorLayer) -> Tuple[int, int, int]:

    feature: QgsFeature

    number_of_features = 0
    complete = 0
    partially_complete = 0

    for feature in layer.getFeatures():

        attributes = feature.attributes()

        attributes_empty = [x != NULL for x in attributes]

        if all(attributes_empty):
            complete += 1
        else:
            partially_complete += 1

        number_of_features += 1

    return number_of_features, complete, partially_complete


def evaluate_result_layer(layer: QgsVectorLayer) -> Tuple[bool, str]:

    number_of_features, complete, partially_complete = evaluate_data_completeness(layer)

    is_complete = False

    message: str

    if number_of_features == complete:

        is_complete = True

        message = TextConstants.msg_result_data_ok

    else:

        is_complete = False

        message = TextConstants.msg_result_data_missing

    return is_complete, message


def get_unique_fields_combinations(layer: QgsVectorLayer,
                                   field_names: List[str]) -> List[List[Any]]:

    feature: QgsFeature

    list_of_unique_combinations = []

    for feature in layer.getFeatures():

        feature_list = []

        for field_name in field_names:

            value = feature.attribute(field_name)

            if value == NULL:
                feature_list.append(None)
            else:
                feature_list.append(value)

        if feature_list not in list_of_unique_combinations:
            list_of_unique_combinations.append(feature_list)

    return list_of_unique_combinations
