from pathlib import Path

from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import QWidget, QSlider, QLabel
from qgis.PyQt import QtCore


class QWidgetSliderValues(QWidget):

    slider_value: QSlider
    label_min = QLabel
    label_max = QLabel

    value_changed = QtCore.pyqtSignal(float)

    def __init__(self, minimum, maximum, current_value):

        super().__init__()

        ui_file = Path(__file__).parent.parent / "ui" / "QWidget_slider.ui"

        uic.loadUi(ui_file.absolute(), self)

        self.slider_min = 0
        self.slider_max = 100
        self.slider_step = 1

        self.min = minimum
        self.max = maximum
        self.val = current_value

        self.label_min.setText(str(self.min))
        self.label_max.setText(str(self.max))

        self.slider_value.setMinimum(self.slider_min)
        self.slider_value.setMaximum(self.slider_max)
        self.slider_value.setSingleStep(self.slider_step)

        if self.min != self.max:
            self.slider_value.setValue(self.recalculate_to_slider(self.val))

            self.slider_value.valueChanged.connect(self._value_changed)
        else:
            self.slider_value.setEnabled(False)
            self.slider_value.setValue(self.min)

    def recalculate_to_slider(self, value: float) -> int:
        result = ((value - self.min) / (self.max - self.min)) * (self.slider_max - self.slider_min) + self.slider_min
        return int(result)

    def recalculate_to_real(self, value: int) -> float:
        result = ((value - self.slider_min) / (self.slider_max - self.slider_min)) * (self.max - self.min) + self.min
        return result

    def _value_changed(self):
        self.val = self.recalculate_to_real(self.slider_value.value())
        self.value_changed.emit(self.val)

    def value(self):
        return self.val

