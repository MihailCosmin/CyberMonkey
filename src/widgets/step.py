import sys
from sys import executable

from os.path import dirname
from os.path import splitext
from os.path import basename
from os.path import realpath

from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QFrame

from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QDrag
from PySide6.QtGui import QPixmap

from PySide6.QtCore import Qt
from PySide6.QtCore import QMimeData

from automonkey import ALL_ACTIONS

from .head import MonkeyHead

exe = ''
if splitext(basename(__file__))[1] == '.pyw'\
        or splitext(basename(__file__))[1] == '.py':
    exe = dirname(realpath(__file__))
elif splitext(basename(__file__))[1] == '.exe':
    exe = dirname(executable)
sys.path.append(exe)

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
        self.handle_button.clicked.connect(self.mouseMoveEvent)
        self.widget.left_layout.addWidget(self.handle_button)
        self.delete_step_button = QPushButton()
        self.delete_step_button.setObjectName("delete_step_button")
        self.widget.right_layout.addWidget(self.delete_step_button)
        self.delete_step_button.setToolTip("Delete step")
        self.delete_step_button.clicked.connect(self.delete_step)

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
        self._make_step()

    def _make_step(self):
        self.action = QComboBox()
        for action in ALL_ACTIONS:
            self.action.addItem(action)

        self.target = QLineEdit()
        self.target.setToolTip(self.target.text())
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
        """get_step_info

        Returns:
            dict: dictinary with step info
        """
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

    def delete_step(self):
        """delete_step
        """
        confirmation = QMessageBox.question(self, "Delete step", "Are you sure you want to delete this step?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.deleteLater()

    def mouseMoveEvent(self, e):
        if isinstance(e, QMouseEvent):
            if e.buttons() == Qt.LeftButton:
                drag = QDrag(self)
                mime = QMimeData()
                drag.setMimeData(mime)

                pixmap = QPixmap(self.size())
                self.render(pixmap)
                drag.setPixmap(pixmap)

                drag.exec(Qt.MoveAction)
