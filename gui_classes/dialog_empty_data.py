from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QLabel

from ..constants import TextConstants
from ..algorithms.utils import is_valid_path_for_file, log


class DialogEmptyData(QDialog):

    label_text_delete: QLabel

    def __init__(self, parent=None):

        super().__init__(parent)

        ui_file = Path(__file__).parent.parent / "ui" / "dialog_data_empty.ui"

        uic.loadUi(ui_file.absolute().as_posix(), self)

        self.setWindowTitle(TextConstants.dialog_empty_title)

        self.label_text_delete.setText(TextConstants.dialog_empty_label)
