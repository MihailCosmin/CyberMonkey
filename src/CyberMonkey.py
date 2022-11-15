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

from shutil import copy
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

        self.setAcceptDrops(True)

        # TODO: 1. Implement config - For ex: ask confirmation for delete step should have a checkbox, don't ask again. This should be saved in a config file
        # TODO: 2. Maybe add multi click get coords and create steps for each click
        # TODO: 3. Add run automation - In progress - To be fully checked
        # TODO: 4. Far future implement scripting. Option to include python sequences between steps.
        # TODO: 5. Add Export to python


        with open("src/qss/light.qss", "r", encoding="utf-8") as _:
            stylesheet = _.read()
        self.setStyleSheet(stylesheet)

        self.menu = self.menuBar().addMenu("File")
        self.menu.addAction("Open")

        self.menu.addAction("Save")
        self.menu.addAction("Save As")
        self.menu.addAction("Export Standalone Steps")
        self.menu.addAction("Import Standalone Steps")

        self.menu.actions()[0].triggered.connect(self.on_open_clicked)  # Open
        self.menu.actions()[0].setShortcut("Ctrl+O")
        self.menu.actions()[1].triggered.connect(self.on_save_clicked)  # Save
        self.menu.actions()[1].setShortcut("Ctrl+S")
        self.menu.actions()[2].triggered.connect(self.on_save_as_clicked)  # Save As
        self.menu.actions()[2].setShortcut("Ctrl+Shift+S")
        self.menu.actions()[3].triggered.connect(self.on_export_standalone_clicked)  # Export Standalone Steps
        self.menu.actions()[3].setShortcut("Ctrl+Shift+E")
        self.menu.actions()[4].triggered.connect(self.on_import_standalone_clicked)  # Import Standalone Steps
        self.menu.actions()[4].setShortcut("Ctrl+Shift+I")

        self.menu = self.menuBar().addMenu("Edit")
        self.menu.addAction("Settings")

        # self.menu.actions()[0].triggered.connect()  # Settings
        self.menu.actions()[0].setShortcut("Ctrl+Shift+S")

        self.menu = self.menuBar().addMenu("Run")
        self.menu.addAction("Run Automation")
        self.menu.addAction("Simulate Automation")
        self.menu.addAction("Stop Automation")
        self.menu.addAction("Record")

        self.menu.actions()[0].triggered.connect(self.on_run_clicked)  # Run Automation
        self.menu.actions()[0].setShortcut("Ctrl+Shift+R")

        self.menu = self.menuBar().addMenu("Help")
        self.menu.addAction("Documentation")
        self.menu.addAction("About")

        self.menu.actions()[0].setShortcut("Ctrl+F1")
        self.menu.actions()[1].setShortcut("Ctrl+Shift+A")

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

    def on_open_clicked(self, override_json: str = None):
        if not override_json:
            self.steps_json = QFileDialog.getOpenFileName(self, "Select File", None, "JSON (*.json)")[0]
            with open(self.steps_json, "r") as f:
                self.steps = load(f)
        else:
            self.steps_json = override_json
            with open(self.steps_json, "r") as f:
                self.steps = load(f)


        if override_json:
            for step in self.steps.values():
                if isfile(join(dirname(self.steps_json), step["target"])):
                    step["target"] = join(dirname(self.steps_json), step["target"])

        if self.steps:
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

    def on_save_clicked(self, override_json: str = None):
        if self.steps_json:
            if not self.steps:
                self._make_steps()
            with open(self.steps_json, "w", encoding="utf-8") as f:
                dump(self.steps, f, indent=4)
        elif override_json:
            if not self.steps:
                self._make_steps()
            with open(override_json, "w", encoding="utf-8") as f:
                dump(self.steps, f, indent=4)
        elif not self.steps_json:
            self.on_save_as_clicked()

    def on_export_standalone_clicked(self):
        standalone_export = normpath(QFileDialog.getSaveFileName(self, "Select File", None, "MonkeySteps (*.monkeysteps)")[0])
        if standalone_export:
            monkey_path = dirname(standalone_export)
            monkey_name = basename(standalone_export).split(".")[0]
            if not isdir(join(monkey_path, monkey_name)):
                mkdir(join(monkey_path, monkey_name))

            if not self.steps:
                self._make_steps()
            for target in [target["target"] for target in self.steps.values() if isfile(target["target"])]:
                copy(target, join(monkey_path, monkey_name, basename(target)))

            _ = {}
            for key, step in self.steps.items():
                _[key] = {}
                for key2, value2 in step.items():
                    if key2 == "target":
                        _[key][key2] = basename(value2)
                    else:
                        _[key][key2] = value2

            _, self.steps = self.steps, _

            self.on_save_clicked(join(monkey_path, monkey_name, "steps.json"))

            self.steps = _
            _ = None

            with SevenZipFile(standalone_export.replace(".monkeysteps", ".7z"), 'w', password='M0nkey_busine$$') as archive:
                archive.writeall(join(monkey_path, monkey_name), ".")

            rename(standalone_export.replace(".monkeysteps", ".7z"), standalone_export)
            if isdir(join(monkey_path, monkey_name)):
                rmtree(join(monkey_path, monkey_name), ignore_errors=True)

    def on_import_standalone_clicked(self):
        standalone_import = normpath(QFileDialog.getOpenFileName(self, "Select File", None, "MonkeySteps (*.monkeysteps)")[0])
        if standalone_import and isfile(standalone_import):
            if not isdir(join(exe, "steps")):
                mkdir(join(exe, "steps"))
            if not isdir(join(exe, "steps", basename(standalone_import).split(".")[0])):
                mkdir(join(exe, "steps", basename(standalone_import).split(".")[0]))
            copy(standalone_import, join(exe, "steps", basename(standalone_import).split(".")[0], basename(standalone_import)))

            seven_zip = join(exe, "steps", basename(standalone_import).split(".")[0], basename(standalone_import)).replace(".monkeysteps", ".7z")
            rename(join(exe, "steps", basename(standalone_import).split(".")[0], basename(standalone_import)), seven_zip)

            with SevenZipFile(seven_zip, mode='r', password='M0nkey_busine$$') as archive:
                archive.extractall(path=seven_zip.replace(basename(seven_zip), ""))
            self.on_open_clicked(seven_zip.replace(basename(seven_zip), "steps.json"))

    def on_run_clicked(self):
        self._make_steps()
        chain(*_clean_steps(self.steps).values(), debug=True)

    def _make_steps(self):
        self.steps = {}
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
