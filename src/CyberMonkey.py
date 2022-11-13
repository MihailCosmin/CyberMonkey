import sys
from sys import executable

from os import mkdir
from os import rename
from os.path import join
from os.path import isdir
from os.path import isfile
from os.path import dirname
from os.path import normpath
from os.path import splitext
from os.path import basename
from os.path import realpath

from json import dump
from json import load

from shutil import copyfile
from shutil import rmtree

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QFrame

from PySide6.QtGui import QIcon

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtCore import Signal

from py7zr import SevenZipFile

from automonkey import chain

exe = ''
if splitext(basename(__file__))[1] == '.pyw'\
        or splitext(basename(__file__))[1] == '.py':
    exe = dirname(realpath(__file__))
elif splitext(basename(__file__))[1] == '.exe':
    exe = dirname(executable)
sys.path.append(exe)

from widgets.step import MonkeyStep
from utils.common import _clean_steps

class CyberMonkey(QMainWindow):

    orderChanged = Signal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberMonkey")
        self.setFixedSize(700, 1000)

        icon = QIcon()
        icon.addFile('src/img/ico/monkey.ico')
        self.setWindowIcon(icon)

        self.steps = {}
        self.steps_json = None
        self.standalone_export = None

        self.setAcceptDrops(True)

        # TODO: Add run automation - In progress - To be fully checked
        # TODO: Possibily add way to move steps up and down - In progress - To be finalized
        # TODO: Add button to browse for image file for target - In progress - See if possible to display only filename, but hold fullpath somewhere
        # TODO: Add button to take screenshot and save to file for target - In progress
        # TODO: Add button to track mouse position and display coords for target - In progress
        # TODO: Add button to track mouse position and get coords when clicked or (ctrl + click)
        # TODO: We need a way to keep image files together with the json file. Probably a zip file (with password)

        with open("src/qss/light.qss", "r", encoding="utf-8") as _:
            stylesheet = _.read()
        self.setStyleSheet(stylesheet)

        self.menu = self.menuBar().addMenu("File")
        self.menu.addAction("Open")
        self.menu.addAction("Save")
        self.menu.addAction("Save As")
        self.menu.addAction("Export Standalone Steps")

        self.menu.actions()[0].triggered.connect(self.on_open_clicked)  # Open
        self.menu.actions()[1].triggered.connect(self.on_save_clicked)  # Save
        self.menu.actions()[2].triggered.connect(self.on_save_as_clicked)  # Save As
        self.menu.actions()[3].triggered.connect(self.on_export_standalone_clicked)  # Export Standalone Steps

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

    def on_export_standalone_clicked(self):
        self.standalone_export = normpath(QFileDialog.getSaveFileName(self, "Select File", None, "MonkeySteps (*.monkeysteps)")[0])
        if self.standalone_export:
            monkey_path = dirname(self.standalone_export)
            monkey_name = basename(self.standalone_export).split(".")[0]
            if not isdir(join(monkey_path, monkey_name)):
                mkdir(join(monkey_path, monkey_name))

            for target in [target["target"] for target in self.steps.values() if isfile(target["target"])]:
                copyfile(target, join(monkey_path, monkey_name, basename(target)))

            # TODO: As a standalone the image path should be relative to steps.json
            self.on_save_clicked(join(monkey_path, monkey_name, "steps.json"))

            with SevenZipFile(self.standalone_export.replace(".monkeysteps", ".7z"), 'w', password='M0nkey_busine$$') as archive:
                archive.writeall(join(monkey_path, monkey_name))

            rename(self.standalone_export.replace(".monkeysteps", ".7z"), self.standalone_export)
            if isdir(join(monkey_path, monkey_name)):
                rmtree(join(monkey_path, monkey_name), ignore_errors=True)

    def on_save_clicked(self, override_json: str = None):
        if self.steps_json:
            self._make_steps()
            with open(self.steps_json, "w", encoding="utf-8") as f:
                dump(self.steps, f, indent=4)
        elif override_json:
            self._make_steps()
            with open(override_json, "w", encoding="utf-8") as f:
                dump(self.steps, f, indent=4)

    def on_run_clicked(self):
        if self.steps is None or len(self.steps) == 0:
            self._make_steps()
        chain(*_clean_steps(self.steps).values(), debug=True)

    def _make_steps(self):
        for i in range(self.monkey_layout.count()):
            step = self.monkey_layout.itemAt(i).widget()
            if isinstance(step, MonkeyStep):
                self.steps[i] = step.get_step_info()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        pos = event.pos()
        widget = event.source()

        for num in range(self.monkey_layout.count()):
            num_widget = self.monkey_layout.itemAt(num).widget()

            if num_widget:
                drop_here = pos.y() < num_widget.y() + num_widget.size().height() // 2
            else:
                drop_here = "last"

            if drop_here:
                if num > 0:
                    self.monkey_layout.insertWidget(num - 1, widget)
                else:
                    self.monkey_layout.insertWidget(num, widget)
                break
            if drop_here == "last":
                self.monkey_layout.insertWidget(self.monkey_layout.count() - 2, widget)

        event.accept()

    def add_item(self, item):
        self.monkey_layout.addWidget(item)

if __name__ == "__main__":
    app = QApplication([])

    import ctypes
    APP_ID = u'mihailcosminmunteanu.monkeybusiness.cybermonkey.001'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

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
