from typing import List, Dict
from pathlib import Path
import configparser
from datetime import datetime

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel

from ..constants import TextConstants
from ..classes.catalog import E3dCatalog
from ..algorithms.utils import log
from ..algorithms.utils import eval_string_with_variables


class DialogAbout(QDialog):

    label_header: QLabel
    label_info: QLabel
    label_footer: QLabel

    def __init__(self,
                 parent=None):

        super().__init__(parent)

        ui_file = Path(__file__).parent.parent / "ui" / "dialog_about.ui"

        uic.loadUi(ui_file.absolute().as_posix(), self)

        config_file = Path(__file__).parent.parent / "metadata.txt"

        config = configparser.ConfigParser()
        config.read(config_file)

        date = datetime.strptime(config['general']['date'], "%Y-%m-%d")

        version = config['general']['version']

        day = date.day
        month = date.month
        year = date.year

        catalog_version = E3dCatalog().get_catalog_version()
        log(catalog_version)

        self.setWindowTitle(TextConstants.dialog_about_header)

        self.label_header.setText(TextConstants.dialog_about_header)

        info = eval_string_with_variables(TextConstants.dialog_about_info)

        self.label_info.setText(info)

        self.label_footer.setText(TextConstants.dialog_about_footer)
