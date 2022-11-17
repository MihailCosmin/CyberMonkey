from os.path import isfile

from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel

from PySide6.QtCore import QThreadPool

from automonkey import PositionTracker

from utils.monkeyshot import MonkeyShot

from automonkey import ALL_ACTIONS
from automonkey import MOUSE_ACTIONS
from automonkey import KEYBOARD_ACTIONS
from automonkey import WAIT_ACTIONS
from automonkey import APPS_ACTIONS
from automonkey import IMG_ACTIONS

class MonkeyHead(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setObjectName("monkey_head")

        self.threadpool = QThreadPool()
        self.worker = None

        self.img_target = None

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self._make_head()

        self._create_buttons()

        self.main_layout.addWidget(self.action)
        self.main_layout.addWidget(self.mouse_actions_button)
        self.main_layout.addWidget(self.keyboard_actions_button)
        self.main_layout.addWidget(self.app_actions_button)
        self.main_layout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addWidget(self.target)
        self.main_layout.addWidget(self.browse_img_button)
        self.main_layout.addWidget(self.screenshot_button)
        self.main_layout.addWidget(self.coordinates_button)
        self.main_layout.addWidget(self.get_coordinates_button)
        self.main_layout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
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

    def _make_head(self):
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

        self.action.setFixedWidth(35)
        self.target.setFixedWidth(40)
        self.wait.setFixedWidth(30)
        self.skip.setFixedWidth(60)
        self.v_offset.setFixedWidth(30)
        self.h_offset.setFixedWidth(30)
        self.offset.setFixedWidth(30)
        self.confidence.setFixedWidth(30)
        self.monitor.setFixedWidth(30)

    def _create_buttons(self):
        self.mouse_actions_button = QPushButton()
        self.mouse_actions_button.setObjectName("mouse_actions_button")
        self.mouse_actions_button.setToolTip("Toggle Mouse Actions Only")
        self.mouse_actions_button.clicked.connect(
            lambda: self.toggle_actions(MOUSE_ACTIONS, self.mouse_actions_button, "mouse"))

        self.keyboard_actions_button = QPushButton()
        self.keyboard_actions_button.setObjectName("keyboard_actions_button")
        self.keyboard_actions_button.setToolTip("Toggle Keyboard Actions Only")
        self.keyboard_actions_button.clicked.connect(
            lambda: self.toggle_actions(KEYBOARD_ACTIONS, self.keyboard_actions_button, "keyboard"))

        self.app_actions_button = QPushButton()
        self.app_actions_button.setObjectName("app_actions_button")
        self.app_actions_button.setToolTip("Toggle App Actions Only")
        self.app_actions_button.clicked.connect(
            lambda: self.toggle_actions(APPS_ACTIONS + IMG_ACTIONS + WAIT_ACTIONS, self.app_actions_button, "app"))

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
        self.coordinates_button.clicked.connect(self.track_mouse)

        self.get_coordinates_button = QPushButton()
        self.get_coordinates_button.setObjectName("get_coordinates_button")
        self.get_coordinates_button.setToolTip("Get coordinates from cursor")
        self.get_coordinates_button.clicked.connect(self.get_coords)

    def track_mouse(self):
        tracker = PositionTracker()
        tracker.start(get_coords=False)

    def get_coords(self):
        tracker = PositionTracker()
        coords = tracker.start(get_coords=True)

        self.parent.target.setText(f"{coords.x}, {coords.y}")
        self.parent.target.setCursorPosition(len(f"{coords.x}, {coords.y}"))

    def browse_img(self):
        self.img_target = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)")[0]
        if self.img_target and isfile(self.img_target):
            self.parent.target.setText(self.img_target)
            self.parent.target.setCursorPosition(len(self.img_target))

    def take_screenshot(self):
        monkeyshot = MonkeyShot()
        scrn = monkeyshot.shoot(mode='dynamic')
        location = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "Image Files (*.png *.jpg *.bmp *.tiff)")[0]
        scrn.save(location)
        self.parent.target.setText(location)
        self.parent.target.setCursorPosition(len(location))
        monkeyshot = None

    def toggle_actions(self, new_list: tuple, button: QPushButton, svg_name: str):
        self.clear_action_toggle_style()
        if len([self.parent.action.itemText(i) for i in range(self.parent.action.count())]) != len(new_list):
            self.parent.action.clear()
            for action in new_list:
                self.parent.action.addItem(action)

            button.setStyleSheet(
                '#monkey_head QPushButton#' + svg_name + '_actions_button {\
                background: transparent;\
                image: url("./src/img/svg/' + svg_name + '_hover.svg");\
                height: 16px;\
                width: 16px;\
                padding-left: 10px;}'
            )
        else:
            self.parent.action.clear()
            for action in ALL_ACTIONS:
                self.parent.action.addItem(action)

            button.setStyleSheet(
                '#monkey_head QPushButton#' + svg_name + '_actions_button {\
                background: transparent;\
                image: url("./src/img/svg/' + svg_name + '.svg");\
                height: 16px;\
                width: 16px;\
                padding-left: 10px;}\
                #monkey_head QPushButton#' + svg_name + '_actions_button:hover {\
                background: transparent;\
                image: url("./src/img/svg/' + svg_name + '_hover.svg");\
                height: 16px;\
                width: 16px;\
                padding-left: 10px;}'
            )

    def clear_action_toggle_style(self):
        action_toggle = {
            'mouse': self.mouse_actions_button,
            'keyboard': self.keyboard_actions_button,
            'app': self.app_actions_button
        }
        for svg_name, button in action_toggle.items():
            button.setStyleSheet(
                '#monkey_head QPushButton#' + svg_name + '_actions_button {\
                background: transparent;\
                image: url("./src/img/svg/' + svg_name + '.svg");\
                height: 16px;\
                width: 16px;\
                padding-left: 10px;}\
                #monkey_head QPushButton#' + svg_name + '_actions_button:hover {\
                background: transparent;\
                image: url("./src/img/svg/' + svg_name + '_hover.svg");\
                height: 16px;\
                width: 16px;\
                padding-left: 10px;}'
            )
