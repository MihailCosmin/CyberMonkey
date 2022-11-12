from json import dump
from json import load

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QMenu

from PySide6.QtGui import QIcon

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize

from automonkey import ALL_ACTIONS

class CyberMonkey(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberMonkey")
        self.setFixedSize(700, 1000)

        icon = QIcon()
        icon.addFile('src/img/ico/monkey.ico')
        self.setWindowIcon(icon)

        self.steps = {}
        self.steps_json = None

        # TODO: Add run automation 

        self.menu = self.menuBar().addMenu("File")
        self.menu.addAction("Open")
        self.menu.addAction("Save")
        self.menu.addAction("Save As")

        self.menu.actions()[0].triggered.connect(self.on_open_clicked)  # Open
        self.menu.actions()[1].triggered.connect(self.on_save_clicked)  # Save
        self.menu.actions()[2].triggered.connect(self.on_save_as_clicked)  # Save As

        self.menu = self.menuBar().addMenu("Run")
        self.menu.addAction("Run Automation")
        self.menu.addAction("Simulate Automation")
        self.menu.addAction("Stop Automation")
        self.menu.addAction("Record")

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.monkey = QWidget()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.monkey)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.verticalScrollBar().rangeChanged.connect(
            lambda min, max: self.scroll_area.verticalScrollBar().setValue(max)
        )

        self.main_layout.addWidget(self.scroll_area)

        self.monkey_layout = QVBoxLayout(self.monkey)

        self.monkey_layout.addWidget(MonkeyHead())
        self.monkey_layout.addWidget(MonkeyStep())

        self.add_step = QPushButton("Add Step")
        self.add_step.setMaximumWidth(100)
        self.add_step_layout = QHBoxLayout()
        self.add_step_layout.addStretch()
        self.add_step_layout.addWidget(self.add_step)
        self.add_step_layout.addStretch()
        self.add_step.clicked.connect(self.add_step_clicked)
        self.monkey_layout.addLayout(self.add_step_layout)

        self.monkey_layout.addStretch(1)

    def add_step_clicked(self):
        # add a step before the add step button
        self.monkey_layout.insertWidget(self.monkey_layout.count() - 2, MonkeyStep())

    def clear_steps(self):
        for i in range(self.monkey_layout.count()):
            step = self.monkey_layout.itemAt(i).widget()
            if isinstance(step, MonkeyStep):
                step.deleteLater()

    def on_open_clicked(self):
        self.steps_json = QFileDialog.getOpenFileName(self, "Select File", None, "JSON (*.json)")[0]
        with open(self.steps_json, "r") as f:
            self.steps = load(f)

        self.clear_steps()
        for step in self.steps.values():
            self.monkey_layout.insertWidget(self.monkey_layout.count() - 2, MonkeyStep())
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().action.setCurrentText(step["action"])
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().target.setText(step["target"])
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().wait.setText(step["wait"])
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().skip.setCurrentText(step["skip"])
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().v_offset.setText(step["v_offset"])
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().h_offset.setText(step["h_offset"])
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().offset.setText(step["offset"])
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().confidence.setText(step["confidence"])
            self.monkey_layout.itemAt(self.monkey_layout.count() - 3).widget().monitor.setText(step["monitor"])

    def on_save_as_clicked(self):
        self.steps_json = QFileDialog.getSaveFileName(self, "Select File", None, "JSON (*.json)")[0]
        self.on_save_clicked()

    def on_save_clicked(self):
        for i in range(self.monkey_layout.count()):
            step = self.monkey_layout.itemAt(i).widget()
            if isinstance(step, MonkeyStep):
                self.steps[i] = step.get_step_info()

        with open(self.steps_json, "w", encoding="utf-8") as f:
            dump(self.steps, f, indent=4)


class MonkeyHead(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.action = QLabel("Action")
        self.target = QLabel("Target")
        self.wait = QLabel("Wait")
        self.skip = QLabel("Skip")
        self.v_offset = QLabel("V Offset")
        self.h_offset = QLabel("H Offset")
        self.offset = QLabel("Offset")
        self.confidence = QLabel("Confidence")
        self.monitor = QLabel("Monitor")

        self.action.setMaximumWidth(self.width() * 0.22)
        self.target.setMaximumWidth(self.width() * 0.22)
        self.wait.setMaximumWidth(self.width() * 0.06)
        self.skip.setMaximumWidth(self.width() * 0.08)
        self.v_offset.setMaximumWidth(self.width() * 0.08)
        self.h_offset.setMaximumWidth(self.width() * 0.08)
        self.offset.setMaximumWidth(self.width() * 0.08)
        self.confidence.setMaximumWidth(self.width() * 0.1)
        self.monitor.setMaximumWidth(self.width() * 0.08)

        self.main_layout.addWidget(self.action)
        self.main_layout.addWidget(self.target)
        self.main_layout.addWidget(self.wait)
        self.main_layout.addWidget(self.skip)
        self.main_layout.addWidget(self.v_offset)
        self.main_layout.addWidget(self.h_offset)
        self.main_layout.addWidget(self.offset)
        self.main_layout.addWidget(self.confidence)
        self.main_layout.addWidget(self.monitor)

class MonkeyStep(QWidget):
    def __init__(self):
        super().__init__()

        # self add exterior border
        self.setStyleSheet("border: 1px solid black;")

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 5, 0, 5)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        self.main_layout.addLayout(self.top_layout)

        self.step_layout = QHBoxLayout()
        self.step_layout.setContentsMargins(0, 0, 0, 0)
        self.step_layout.setSpacing(0)
        self.main_layout.addLayout(self.step_layout)

        self.action = QComboBox()
        for action in ALL_ACTIONS:
            self.action.addItem(action)

        self.target = QLineEdit()
        self.wait = QLineEdit()
        self.skip = QComboBox()
        self.skip.addItem("False")
        self.skip.addItem("True")
        self.v_offset = QLineEdit()
        self.h_offset = QLineEdit()
        self.offset = QLineEdit()
        self.confidence = QLineEdit()
        self.monitor = QLineEdit()

        self.action.setMaximumWidth(self.width() * 0.22)
        self.target.setMaximumWidth(self.width() * 0.22)
        self.wait.setMaximumWidth(self.width() * 0.06)
        self.skip.setMaximumWidth(self.width() * 0.08)
        self.v_offset.setMaximumWidth(self.width() * 0.08)
        self.h_offset.setMaximumWidth(self.width() * 0.08)
        self.offset.setMaximumWidth(self.width() * 0.08)
        self.confidence.setMaximumWidth(self.width() * 0.1)
        self.monitor.setMaximumWidth(self.width() * 0.08)

        self.step_layout.addWidget(self.action)
        self.step_layout.addWidget(self.target)
        self.step_layout.addWidget(self.wait)
        self.step_layout.addWidget(self.skip)
        self.step_layout.addWidget(self.v_offset)
        self.step_layout.addWidget(self.h_offset)
        self.step_layout.addWidget(self.offset)
        self.step_layout.addWidget(self.confidence)
        self.step_layout.addWidget(self.monitor)

    def get_step_info(self):
        return {
            "action": self.action.currentText(),
            "target": self.target.text(),
            "wait": self.wait.text(),
            "skip": self.skip.currentText(),
            "v_offset": self.v_offset.text(),
            "h_offset": self.h_offset.text(),
            "offset": self.offset.text(),
            "confidence": self.confidence.text(),
            "monitor": self.monitor.text()
        }

if __name__ == "__main__":
    app = QApplication([])

    import ctypes
    myappid = u'mihailcosminmunteanu.monkeybusiness.cybermonkey.001'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app_icon = QIcon()
    app_icon.addFile('src/img/png/monkey_16x16.png', QSize(16, 16))
    app_icon.addFile('src/img/png/monkey_24x24.png', QSize(24, 24))
    app_icon.addFile('src/img/png/monkey_32x32.png', QSize(32, 32))
    app_icon.addFile('src/img/png/monkey_48x48.png', QSize(48, 48))
    app_icon.addFile('src/img/png/monkey_64x64.png', QSize(64, 64))
    app_icon.addFile('src/img/png/monkey_128x128.png', QSize(128, 128))
    app_icon.addFile('src/img/png/monkey_256x256.png', QSize(256, 256))
    app.setWindowIcon(app_icon)

    window = CyberMonkey()
    window.show()
    app.exec()
