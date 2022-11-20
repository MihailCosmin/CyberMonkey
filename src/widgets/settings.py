from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem

class SettingWidget(QWidget):
    def __init__(self, parent=None, setting: str = None, options: list = None, value: str = None, tip: str = None):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setting_label = None
        self.setting_widget = None

        if tip == "combobox":
            self._create_combo_box(setting, options, value)
        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def _create_combo_box(self, setting, options, value):
        self.setting_label = QLabel(setting)
        self.setting_label.setObjectName(f"{setting}_label")
        self.setting_label.setMinimumWidth(140)
        self.setting_widget = QComboBox()
        self.setting_widget.setObjectName(f"{setting}_widget")
        self.setting_widget.setMinimumWidth(200)
        self.setting_widget.addItems(options)
        self.setting_widget.setCurrentText(str(value))
        self.layout.addWidget(self.setting_label)
        self.layout.addWidget(self.setting_widget)

    def _create_line_edit(self, setting, current_text):
        pass

    def _create_browse_file(self, setting):
        pass
