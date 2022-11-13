import sys
from sys import executable

from os.path import isfile
from os.path import dirname
from os.path import splitext
from os.path import basename
from os.path import realpath

from re import search

from json import dump
from json import load

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QFrame

from PySide6.QtGui import QPainterPath
from PySide6.QtGui import QRegion
from PySide6.QtGui import QIcon

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtCore import QRectF
from PySide6.QtCore import QThreadPool

from automonkey import ALL_ACTIONS
from automonkey import chain
from automonkey import PositionTracker

exe = ''
if splitext(basename(__file__))[1] == '.pyw'\
        or splitext(basename(__file__))[1] == '.py':
    exe = dirname(realpath(__file__))
elif splitext(basename(__file__))[1] == '.exe':
    exe = dirname(executable)
sys.path.append(exe)

from monkeyshot import MonkeyShot
from utils.thread import Worker

COORDS_REGEX = r"^\d+, *\d+$"

def _clean_steps(steps: dict) -> dict:
    """Prepare steps for automonkey chain."""
    cleaned = {}
    for key, value in steps.items():
        if not isfile(value["target"]) and search(COORDS_REGEX, value["target"]):
            step = {value["action"]: tuple(map(int, value["target"].split(",")))}
        else:
            step = {value["action"]: value["target"]}
        for key2, value2 in value.items():
            if value2 not in ("", "action", "target"):
                step[key2] = int(value2) if key != "skip" else eval(value2)
        cleaned[key] = step
    return cleaned

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

        # TODO: Add run automation - In progress - To be fully checked
        # TODO: Possibily add way to move steps up and down - In progress - To be finalized
        # TODO: Add button to browse for image file for target - In progress - See if possible to display only filename, but hold fullpath somewhere
        # TODO: Add button to take screenshot and save to file for target - In progress
        # TODO: Add button to track mouse position and display coords for target - In progress
        # TODO: Add button to track mouse position and get coords when clicked or (ctrl + click)

        with open("src/qss/light.qss", "r", encoding="utf-8") as _:
            stylesheet = _.read()
        self.setStyleSheet(stylesheet)

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

        self.menu.actions()[0].triggered.connect(self.on_run_clicked)  # Run Automation

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
        if self.steps_json:
            self.on_save_clicked()

    def on_save_clicked(self):
        if self.steps_json:
            self._make_steps()
            with open(self.steps_json, "w", encoding="utf-8") as f:
                dump(self.steps, f, indent=4)

    def on_run_clicked(self):
        if self.steps is None or len(self.steps) == 0:
            self._make_steps()
        print(self.steps)  
        print(_clean_steps(self.steps))

        chain(*_clean_steps(self.steps).values(), debug=True)

    def _make_steps(self):
        for i in range(self.monkey_layout.count()):
            step = self.monkey_layout.itemAt(i).widget()
            if isinstance(step, MonkeyStep):
                self.steps[i] = step.get_step_info()

class MonkeyHead(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setObjectName("monkey_head")

        self.threadpool = QThreadPool()
        self.worker = None

        self.monkeyshot = None

        self.img_target = None

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.action = QLabel("Action")
        self.action.setToolTip("Action to perform.\nEx: click, write, keys, open_app, minimize.\nSee https://github.com/MihailCosmin/AutoMonkey/blob/main/README.md for more info.")
        self.target = QLabel("Target")
        self.target.setToolTip("Target to perform action on.\nEx: image, coordintaes, text, app name, filename.")
        self.wait = QLabel("Wait")
        self.wait.setToolTip("Time to wait before performing next action.\nEx: 0.1, 0.5, 1, 2, 5.")
        self.skip = QLabel("Skip")  # Skip
        self.skip.setToolTip("Skip action if target is not found.\nTrue, False.")
        self.v_offset = QLabel("V Off")  # Vertical Offset
        self.v_offset.setToolTip("Vertical Offset in pixels.\nEx: 0, 10, 20, 50, 100.")
        self.h_offset = QLabel("H Off")  # Horizontal offset
        self.h_offset.setToolTip("Horizontal Offset in pixels.\nEx: 0, 10, 20, 50, 100.")
        self.offset = QLabel("Off")  # Offset
        self.offset.setToolTip("Offset in pixels.\nEx: 0, 10, 20, 50, 100.")
        self.confidence = QLabel("Conf")  # Confidence
        self.confidence.setToolTip("Confidence, between 0 and 1.\nEx: 0.1, 0.5, 0.9. Recommended: 0.9")
        self.monitor = QLabel("Mon")  # Monitor
        self.monitor.setToolTip("Monitor")

        self.action.setFixedWidth(140)
        self.target.setFixedWidth(40)
        self.wait.setFixedWidth(30)
        self.skip.setFixedWidth(60)
        self.v_offset.setFixedWidth(30)
        self.h_offset.setFixedWidth(30)
        self.offset.setFixedWidth(30)
        self.confidence.setFixedWidth(30)
        self.monitor.setFixedWidth(30)

        self.browse_img_button = QPushButton()
        self.browse_img_button.setObjectName("browse_img_button")
        self.browse_img_button.setToolTip("Browse for image")
        self.browse_img_button.clicked.connect(self.browse_img)
        self.screenshot_button = QPushButton()
        self.screenshot_button.setObjectName("screenshot_button")
        self.screenshot_button.setToolTip("Take a screenshot of a button")
        self.screenshot_button.clicked.connect(self.take_screenshot)
        self.coordinates_button = QPushButton()
        self.coordinates_button.setObjectName("coordinates_button")
        self.coordinates_button.setToolTip("Track mouse coordinates")
        self.coordinates_button.clicked.connect(PositionTracker)

        self.main_layout.addWidget(self.action)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.target)
        self.main_layout.addWidget(self.browse_img_button)
        self.main_layout.addWidget(self.screenshot_button)
        self.main_layout.addWidget(self.coordinates_button)
        self.main_layout.addSpacerItem(QSpacerItem(60, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.wait)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.skip)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.v_offset)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.h_offset)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.offset)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.confidence)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.monitor)

    def browse_img(self):
        self.img_target = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)")[0]
        if self.img_target and isfile(self.img_target):
            self.parent.target.setText(self.img_target)

    def take_screenshot(self):
        self.monkeyshot = MonkeyShot()
        scrn = self.monkeyshot.shoot(mode='dynamic')
        scrn.save("screenshot.png")
        self.monkeyshot = None

class MonkeyStep(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("border: 0px solid white;")
        self.setObjectName("monkey_step")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.frame = QFrame()
        self.frame.setStyleSheet("border: 5px solid darkgray; border-radius: 30px;")

        self.layout.addWidget(self.frame)

        self.widget = QWidget()
        self.frame_layout = QVBoxLayout()
        self.frame.setLayout(self.frame_layout)
        self.frame_layout.addWidget(self.widget)

        self.central_layout = QHBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.widget.setLayout(self.central_layout)

        self.widget.left_layout = QVBoxLayout()
        self.widget.left_layout.setContentsMargins(0, 0, 5, 0)
        self.widget.right_layout = QVBoxLayout()
        self.widget.right_layout.setContentsMargins(5, 0, 0, 0)
        self.widget.main_layout = QVBoxLayout()

        self.central_layout.addLayout(self.widget.left_layout)
        self.central_layout.addLayout(self.widget.main_layout)
        self.central_layout.addLayout(self.widget.right_layout)

        self.handle_button = QPushButton()
        self.handle_button.setObjectName("handle_button")
        self.handle_button.setToolTip("Move step")
        self.widget.left_layout.addWidget(self.handle_button)
        self.delete_step_button = QPushButton()
        self.delete_step_button.setObjectName("delete_step_button")
        self.widget.right_layout.addWidget(self.delete_step_button)
        self.delete_step_button.setToolTip("Delete step")
        self.delete_step_button.clicked.connect(self.deleteLater)

        self.widget.setStyleSheet("border: 0px solid gray;")

        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 5)
        self.top_layout.setSpacing(0)
        self.widget.main_layout.addLayout(self.top_layout)

        self.top_layout.addWidget(MonkeyHead(parent=self))

        self.step_layout = QHBoxLayout()
        self.step_layout.setContentsMargins(0, 0, 0, 0)
        self.step_layout.setSpacing(0)
        self.widget.main_layout.addLayout(self.step_layout)

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

        self.action.setFixedWidth(140)
        self.target.setFixedWidth(160)
        self.wait.setFixedWidth(30)
        self.skip.setFixedWidth(60)
        self.v_offset.setFixedWidth(30)
        self.h_offset.setFixedWidth(30)
        self.offset.setFixedWidth(30)
        self.confidence.setFixedWidth(30)
        self.monitor.setFixedWidth(30)

        self.step_layout.addWidget(self.action)
        self.step_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.step_layout.addWidget(self.target)
        self.step_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.step_layout.addWidget(self.wait)
        self.step_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.step_layout.addWidget(self.skip)
        self.step_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.step_layout.addWidget(self.v_offset)
        self.step_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.step_layout.addWidget(self.h_offset)
        self.step_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.step_layout.addWidget(self.offset)
        self.step_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.step_layout.addWidget(self.confidence)
        self.step_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
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
