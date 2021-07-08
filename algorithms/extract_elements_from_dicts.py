from typing import Dict, Any


def extract_elements_without_values(dict_obj: Dict[str, Any]) -> Dict[str, Any]:

    new_dict = dict()

    for (key, value) in dict_obj.items():
        if value is None:
            new_dict[key] = value

    return new_dict


def extract_elements_with_values(dict_obj: Dict[str, Any]) -> Dict[str, Any]:

    new_dict = dict()

    for (key, value) in dict_obj.items():
        if value is not None:
            new_dict[key] = value

    return new_dict
